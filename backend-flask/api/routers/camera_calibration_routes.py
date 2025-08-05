from asyncio import sleep

from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.responses import JSONResponse
from starlette.websockets import WebSocketDisconnect, WebSocket
from wsproto.utilities import LocalProtocolError

from api.dependencies.services import get_service_by_type
from api.error_handlers import handle_route_errors, validate_authentication
from api.ws_connection_manager import ConnectionManager
from repo.repositories import ImageSourceRepository
from repo.repository_exceptions import UidNotUnique
from services.authorization.authorization import get_current_user
from services.camera_calibration.camera_calibration_models import CameraCalibrationParametersModel
from services.camera_calibration.camera_calibration_service import CameraCalibrationService
from services.image_source.image_source_service import ImageSourceService
from src.utils import frame_to_base64

router = APIRouter(
    tags=["camera_calibration"],
    prefix="/camera_calibration",
)


@router.post("")
@handle_route_errors("set", "CameraCalibration parameters")
async def set_calibration_parameters(
        calibration_parameters: CameraCalibrationParametersModel,
        user: dict = Depends(get_current_user),
        camera_calibration_service: CameraCalibrationService = Depends(get_service_by_type(CameraCalibrationService))
):
    validate_authentication(user, "set camera calibration parameters")
    camera_calibration_service.set_calibration_parameters(calibration_parameters)
    return JSONResponse(status_code=status.HTTP_200_OK, content='')


manager = ConnectionManager()


@router.websocket("/{image_source_uid}/ws/{ws_uid}")
async def websocket_endpoint(
        websocket: WebSocket,
        image_source_uid,
        ws_uid,
        camera_calibration_service: CameraCalibrationService = Depends(get_service_by_type(CameraCalibrationService)),
        image_source_repository: ImageSourceRepository = Depends(get_service_by_type(ImageSourceRepository)),
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService))
):
    await manager.connect(ws_uid, websocket)
    try:
        while True:
            if manager.is_closed(ws_uid):
                break

            data = await websocket.receive_json()

            try:
                if data["command"] == "capture":
                    frame = image_source_service.grab_from_image_source(image_source_uid)
                    camera_calibration_service.save_calibration_frame(frame)
                if data["command"] == "calibrate":
                    try:
                        camera_calibration_service.calibrate_camera()
                        await websocket.send_json({
                            'data': camera_calibration_service.get_rmse(),
                            'details': 'calibDone'
                        })
                    except Exception as e:
                        await websocket.send_json({
                            'data': '',
                            'details': 'calibError'
                        })
                if data["command"] == "retrieve":
                    frame = camera_calibration_service.get_calibration_frame(data["idx"])
                    image = frame_to_base64(frame)
                    await websocket.send_json({
                        'data': image.decode('utf-8'),
                        'details': 'calibFrame'
                    })
                if data["command"] == "save":
                    image_source_dict = image_source_repository.read_id(image_source_uid)

                    if image_source_dict and image_source_dict["camera_calibration_uid"] is not None:
                        camera_calibration_service.delete_calibration(image_source_dict["camera_calibration_uid"])

                    camera_calibration_service.save_calibration_results(data["uid"])
                    image_source_repository.update_field(image_source_uid, "camera_calibration_uid", data["uid"])
                if data["command"] == "stop":
                    break
            except KeyError:
                pass

            await sleep(0.05)

        await manager.disconnect(ws_uid)
    except WebSocketDisconnect:
        await manager.disconnect(ws_uid)
    except LocalProtocolError:
        manager.remove_websocket(ws_uid)
    except RuntimeError:
        pass


@router.post("/{ws_uid}/ws/close")
@handle_route_errors("close", "CameraCalibration WebSocket", "ws_uid")
async def close_ws(ws_uid):
    await manager.connection_closed(ws_uid)
    return JSONResponse(status_code=status.HTTP_200_OK, content='')
