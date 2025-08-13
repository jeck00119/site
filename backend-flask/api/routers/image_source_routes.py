import numpy as np
from anyio import sleep
from typing import List, Dict
from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from wsproto.utilities import LocalProtocolError

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response
from api.route_utils import RouteHelper, require_authentication
from security.validators import validate_input, detect_security_threats, validate_file_upload
from api.ws_connection_manager import ConnectionManager
from repo.repositories import ImageSourceRepository
from repo.repository_exceptions import UidNotFound, UidNotUnique
from services.camera_calibration.camera_calibration_service import CameraCalibrationService
from services.image_source.image_source_model import ImageSourceModel, ImgSrcEnum
from services.image_source.image_source_service import ImageSourceService
from src.utils import frame_to_base64

router = APIRouter(
    tags=["image_source"],
    prefix="/image_source"
)


@router.get("")
async def list_image_sources(
        image_source_repository: ImageSourceRepository = Depends(get_service_by_type(ImageSourceRepository))
) -> JSONResponse:
    try:
        sources = RouteHelper.list_entities(
            image_source_repository,
            "ImageSource"
        )
        resp = []
        for img_src in sources:
            resp.append({
                'uid': img_src['uid'],
                'name': img_src['name']
            })
        return RouteHelper.create_success_response(resp)
    except Exception as e:
        raise create_error_response("list", "ImageSource", exception=e)


@router.get("/{image_source_uid}")
@validate_input(image_source_uid="safe_string")
async def get_image_source(
        image_source_uid: str,
        image_source_repository: ImageSourceRepository = Depends(get_service_by_type(ImageSourceRepository)),
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService))
) -> JSONResponse:
    try:
        entity = RouteHelper.get_entity_by_id(
            image_source_repository,
            image_source_uid,
            "ImageSource"
        )
        image_source_service.load_settings_to_image_source(uid=image_source_uid)
        result = ImageSourceModel(**entity)
        return RouteHelper.create_success_response(result.model_dump())
    except Exception as e:
        raise create_error_response("get", "ImageSource", entity_id=image_source_uid, exception=e)


@router.post("")
@detect_security_threats()
async def post_image_source(
        image_source: ImageSourceModel,
        user: dict = Depends(require_authentication),
        image_source_repository: ImageSourceRepository = Depends(get_service_by_type(ImageSourceRepository))
) -> JSONResponse:
    try:
        RouteHelper.create_entity(
            image_source_repository,
            image_source,
            "ImageSource"
        )
        return RouteHelper.create_success_response("")
    except Exception as e:
        raise create_error_response("create", "ImageSource", exception=e)


@router.put("/{image_source_uid}")
@validate_input(image_source_uid="safe_string")
@detect_security_threats()
async def put_image_source(
        image_source: ImageSourceModel,
        user: dict = Depends(require_authentication),
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        image_source_repository: ImageSourceRepository = Depends(get_service_by_type(ImageSourceRepository))
) -> JSONResponse:
    try:
        RouteHelper.update_entity(
            image_source_repository,
            image_source,
            "ImageSource"
        )
        image_source_service.on_patch_image_source(image_source)
        return RouteHelper.create_success_response("")
    except Exception as e:
        raise create_error_response("update", "ImageSource", entity_id=image_source.uid, exception=e)


@router.delete("/{image_source_uid}")
async def delete_image_source(
        image_source_uid: str,
        user: dict = Depends(require_authentication),
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        image_source_repository: ImageSourceRepository = Depends(get_service_by_type(ImageSourceRepository))
) -> JSONResponse:
    try:
        RouteHelper.delete_entity(
            image_source_repository,
            image_source_uid,
            "ImageSource"
        )
        image_source_service.on_delete_image_source(image_source_uid)
        return RouteHelper.create_success_response("")
    except Exception as e:
        raise create_error_response("delete", "ImageSource", entity_id=image_source_uid, exception=e)


manager = ConnectionManager()


@router.websocket("/{image_source_uid}/ws/{ws_uid}")
async def websocket_endpoint(
        websocket: WebSocket,
        ws_uid,
        image_source_uid,
        image_source_repository: ImageSourceRepository = Depends(get_service_by_type(ImageSourceRepository)),
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        camera_calibration_service: CameraCalibrationService = Depends(get_service_by_type(CameraCalibrationService))
):
    try:
        await manager.connect(ws_uid, websocket)
        
        # Safely read image source configuration
        try:
            image_source = image_source_repository.read_id(image_source_uid)
        except Exception as e:
            print(f"Error reading image source {image_source_uid}: {e}")
            await manager.disconnect(ws_uid)
            return

        if image_source_service.check_image_source_type(image_source_uid) == ImgSrcEnum.DYNAMIC:
            image_source_type = "dynamic"
        elif image_source_service.check_image_source_type(image_source_uid) == ImgSrcEnum.STATIC:
            image_source_type = "static"
            
        while True:
            if manager.is_closed(ws_uid):
                break

            try:
                frame = image_source_service.grab_from_image_source(image_source_uid)
                
                if frame is None:
                    continue

                if image_source.get("camera_calibration_uid"):
                    frame = camera_calibration_service.undistort_image(frame, image_source.get("camera_calibration_uid"))

                # Handle frame encoding with proper error handling
                try:
                    image = frame_to_base64(frame, quality=85)
                    await websocket.send_bytes(image)
                except (ValueError, TypeError) as e:
                    print(f"Frame encoding error for image source {image_source_uid}: {e}")
                    continue
                except Exception as e:
                    print(f"WebSocket send error for {ws_uid}: {e}")
                    break
                    
            except Exception as e:
                print(f"Error grabbing frame from image source {image_source_uid}: {e}")
                continue
                
            try:
                fps = image_source.get('fps', 10)  # Default to 10 FPS if not set
                await sleep(1 / fps)
            except Exception as e:
                print(f"Error in sleep: {e}")
                await sleep(0.1)  # Fallback sleep

        print("Exiting loop...")
        await manager.disconnect(ws_uid)
    except WebSocketDisconnect:
        print("Web socket disconnect")
        await manager.disconnect(ws_uid)
    except LocalProtocolError:
        print("Local protocol error")
        await manager.disconnect(ws_uid)
    except RuntimeError:
        print("Runtime error")
        pass


@router.websocket("/{image_source_uid}/{generator_or_camera_uid}/{fps}/ws/{ws_uid}")
async def websocket_live_image_source_with_fps(
        websocket: WebSocket,
        ws_uid,
        image_source_uid,
        generator_or_camera_uid,
        fps,
        image_source_repository: ImageSourceRepository = Depends(get_service_by_type(ImageSourceRepository)),
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        camera_calibration_service: CameraCalibrationService = Depends(get_service_by_type(CameraCalibrationService))
):
    await manager.connect(ws_uid, websocket)
    image_source = image_source_repository.read_id(image_source_uid)

    if image_source_service.check_image_source_type(image_source_uid) == ImgSrcEnum.DYNAMIC:
        image_source_type = "dynamic"
    elif image_source_service.check_image_source_type(image_source_uid) == ImgSrcEnum.STATIC:
        image_source_type = "static"

    try:
        while True:
            # data = await websocket.receive_text()
            if manager.is_closed(ws_uid):
                break

            try:
                image = np.zeros(shape=(640, 480, 3), dtype=np.uint8)
                if image_source_type == "dynamic":
                    image = image_source_service.camera_service.grab_from_camera(generator_or_camera_uid)

                    if image_source.get("camera_calibration_uid"):
                        image = camera_calibration_service.undistort_image(image,
                                                                           image_source.get("camera_calibration_uid"))
                elif image_source_type == "static":
                    image = image_source_service.image_generator_service.grab_from_generator(generator_or_camera_uid)
                
                image_source_service.images_sources_last_frame[image_source_uid] = image
                
                # Handle frame encoding with proper error handling
                try:
                    image_bytes = frame_to_base64(image, quality=85)
                    await websocket.send_bytes(image_bytes)
                except (ValueError, TypeError) as e:
                    print(f"Frame encoding error for image source {image_source_uid}: {e}")
                    # Skip this frame and continue with next one
                    continue
                except Exception as e:
                    print(f"WebSocket send error for {ws_uid}: {e}")
                    # WebSocket connection is likely closed, break the loop
                    break
                    
            except Exception as e:
                print(f"Error processing frame for image source {image_source_uid}: {e}")
                # Continue loop to try again
                continue

            await sleep(1 / int(fps))

        await manager.disconnect(ws_uid)
    except WebSocketDisconnect:
        await manager.disconnect(ws_uid)
    except LocalProtocolError:
        manager.remove_websocket(ws_uid)
    except RuntimeError:
        pass


@router.post("/{ws_uid}/ws/close")
async def close_ws(ws_uid: str) -> JSONResponse:
    try:
        await manager.connection_closed(ws_uid)
        return RouteHelper.create_success_response("")
    except Exception as e:
        raise create_error_response("close_ws", "ImageSource", exception=e)
