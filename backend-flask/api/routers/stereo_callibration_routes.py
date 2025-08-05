from asyncio import sleep

import numpy as np
from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.responses import JSONResponse
from starlette.websockets import WebSocketDisconnect, WebSocket
from tinydb import Query

from wsproto.utilities import LocalProtocolError

from api.dependencies.services import get_service_by_type
from api.error_handlers import handle_route_errors, validate_authentication
from api.ws_connection_manager import ConnectionManager
from repo.repositories import ImageSourceRepository, StereoCalibrationRepository, CameraCalibrationRepository
from repo.repository_exceptions import UidNotUnique
from services.authorization.authorization import get_current_user
from services.camera_calibration.camera_calibration_models import CameraCalibrationParametersModel, \
    CameraIntrinsicsModel
from services.image_source.image_source_service import ImageSourceService
from services.stereo_calibration.stereo_calibration_models import StereoResultsModel
from services.stereo_calibration.stereo_calibration_service import StereoCalibrationService
from src.utils import frame_to_base64

router = APIRouter(
    tags=["stereo_calibration"],
    prefix="/stereo_calibration",
)


@router.post("")
@handle_route_errors("set", "StereoCalibration parameters")
async def set_calibration_parameters(
        calibration_parameters: CameraCalibrationParametersModel,
        user: dict = Depends(get_current_user),
        stereo_calibration_service: StereoCalibrationService = Depends(get_service_by_type(StereoCalibrationService))
):
    validate_authentication(user, "set stereo calibration parameters")
    stereo_calibration_service.set_calibration_parameters(calibration_parameters)
    return JSONResponse(status_code=status.HTTP_200_OK, content='')


manager = ConnectionManager()


@router.websocket("/{first_image_source_uid}/{second_image_source_uid}/ws/{ws_uid}")
async def websocket_endpoint(
        websocket: WebSocket,
        first_image_source_uid,
        second_image_source_uid,
        ws_uid,
        stereo_calibration_service: StereoCalibrationService = Depends(get_service_by_type(StereoCalibrationService)),
        image_source_repository: ImageSourceRepository = Depends(get_service_by_type(ImageSourceRepository)),
        camera_calibration_repository: CameraCalibrationRepository = Depends(
            get_service_by_type(CameraCalibrationRepository)),
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        stereo_calibration_repository: StereoCalibrationRepository = Depends(
            get_service_by_type(StereoCalibrationRepository))
):
    await manager.connect(ws_uid, websocket)
    try:
        while True:
            if manager.is_closed(ws_uid):
                break

            data = await websocket.receive_json()

            try:
                if data["command"] == "capture":
                    first_frame = image_source_service.grab_from_image_source(first_image_source_uid)
                    second_frame = image_source_service.grab_from_image_source(second_image_source_uid)
                    stereo_calibration_service.save_calibration_frame_pair(first_frame, second_frame)
                if data["command"] == "calibrate":
                    try:
                        image_source_dict = image_source_repository.read_id(first_image_source_uid)
                        first_camera_intrinsics_dict = camera_calibration_repository.read_id(
                            image_source_dict["camera_calibration_uid"])
                        first_camera_intrinsics_model = CameraIntrinsicsModel(**first_camera_intrinsics_dict)

                        image_source_dict = image_source_repository.read_id(second_image_source_uid)
                        second_camera_intrinsics_dict = camera_calibration_repository.read_id(
                            image_source_dict["camera_calibration_uid"])
                        second_camera_intrinsics_model = CameraIntrinsicsModel(**second_camera_intrinsics_dict)

                        stereo_calibration_service.stereo_calibrate(
                            cam_mtx1=np.asarray(first_camera_intrinsics_model.camera_matrix),
                            dist1=np.asarray(first_camera_intrinsics_model.distortion_coeffs),
                            cam_mtx2=np.asarray(second_camera_intrinsics_model.camera_matrix),
                            dist2=np.asarray(second_camera_intrinsics_model.distortion_coeffs))
                        await websocket.send_json({
                            'data': stereo_calibration_service.get_rmse(),
                            'details': 'calibDone'
                        })
                    except Exception as e:
                        await websocket.send_json({
                            'data': str(e),
                            'details': 'calibError'
                        })
                if data["command"] == "retrieve":
                    first_img_src_frame, second_img_src_frame = stereo_calibration_service.get_calibration_frame_pair(
                        data["idx"])

                    result = [frame_to_base64(first_img_src_frame).decode('utf-8'),
                              frame_to_base64(second_img_src_frame).decode('utf-8')]
                    await websocket.send_json({
                        'data': result,
                        'details': 'calibFrame'
                    })
                if data["command"] == "save":
                    stereo_calibration_service.save_calibration_results(data["uid"], first_image_source_uid,
                                                                        second_image_source_uid)

                if data["command"] == "origin":
                    first_frame = image_source_service.grab_from_image_source(first_image_source_uid)
                    second_frame = image_source_service.grab_from_image_source(second_image_source_uid)

                    image_source_dict = image_source_repository.read_id(first_image_source_uid)
                    first_camera_intrinsics_dict = camera_calibration_repository.read_id(
                        image_source_dict["camera_calibration_uid"])
                    first_camera_intrinsics_model = CameraIntrinsicsModel(**first_camera_intrinsics_dict)

                    image_source_dict = image_source_repository.read_id(second_image_source_uid)
                    second_camera_intrinsics_dict = camera_calibration_repository.read_id(
                        image_source_dict["camera_calibration_uid"])
                    second_camera_intrinsics_model = CameraIntrinsicsModel(**second_camera_intrinsics_dict)

                    RW0, TW0, RW1, TW1 = stereo_calibration_service.set_world_frame_origin(
                        left_frame=first_frame,
                        right_frame=second_frame,
                        left_camera_matrix=np.asarray(first_camera_intrinsics_model.camera_matrix),
                        left_camera_distortion=np.asarray(first_camera_intrinsics_model.distortion_coeffs),
                        right_camera_matrix=np.asarray(second_camera_intrinsics_model.camera_matrix),
                        right_camera_distortion=np.asarray(second_camera_intrinsics_model.distortion_coeffs))

                    q = Query()
                    stereo_results_dict = stereo_calibration_repository.find_by_query(
                        (q.first_image_src_uid == first_image_source_uid) & (
                                q.second_image_src_uid == second_image_source_uid))

                    if stereo_results_dict:
                        stereo_results_model = StereoResultsModel(**stereo_results_dict[0])

                        stereo_results_model.world_to_cam_left_rot = RW0.tolist()
                        stereo_results_model.world_to_cam_left_trans = TW0.tolist()
                        stereo_results_model.world_to_cam_right_rot = RW1.tolist()
                        stereo_results_model.world_to_cam_right_trans = TW1.tolist()

                        stereo_calibration_repository.update(stereo_results_model)

                        await websocket.send_json({
                            'data': '',
                            'details': 'originDone'
                        })
                if data["command"] == "stop":
                    break
            except KeyError:
                pass

            await sleep(0.05)

        await manager.disconnect(ws_uid)
    except WebSocketDisconnect:
        await manager.disconnect(ws_uid)
    except LocalProtocolError:
        await manager.disconnect(ws_uid)
    except RuntimeError:
        manager.remove_websocket(ws_uid)


@router.post("/{ws_uid}/ws/close")
@handle_route_errors("close", "StereoCalibration WebSocket", "ws_uid")
async def close_ws(ws_uid):
    await manager.connection_closed(ws_uid)
    return JSONResponse(status_code=status.HTTP_200_OK, content='')
