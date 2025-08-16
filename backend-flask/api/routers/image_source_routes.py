import numpy as np
from anyio import sleep
from typing import List, Dict
from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from wsproto.utilities import LocalProtocolError

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response, handle_route_errors
from api.route_utils import RouteHelper, require_authentication, get_repository_and_config_service
from security.validators import validate_input, detect_security_threats, validate_file_upload
from api.ws_connection_manager import ConnectionManager
from repo.repositories import ImageSourceRepository
from repo.repository_exceptions import UidNotFound, UidNotUnique
from services.camera_calibration.camera_calibration_service import CameraCalibrationService
from services.configurations.configurations_service import ConfigurationService
from services.image_source.image_source_model import ImageSourceModel, ImgSrcEnum
from services.image_source.image_source_service import ImageSourceService
from src.utils import frame_to_base64

router = APIRouter(
    tags=["image_source"],
    prefix="/image_source"
)


@router.get("")
@handle_route_errors("list", "ImageSource")
async def list_image_sources(
        _: dict = Depends(require_authentication("list image sources")),
        repo_and_config=Depends(get_repository_and_config_service(ImageSourceRepository))
) -> List[Dict[str, str]]:
    image_source_repository, configuration_service = repo_and_config
    sources = RouteHelper.list_entities_with_config_context(
        image_source_repository,
        configuration_service,
        "ImageSource"
    )
    return RouteHelper.transform_list_to_uid_name(sources)


@router.get("/{image_source_uid}")
@validate_input(image_source_uid="safe_string")
@handle_route_errors("retrieve", "ImageSource", "image_source_uid")
async def get_image_source(
        image_source_uid: str,
        _: dict = Depends(require_authentication("get image source")),
        repo_and_config=Depends(get_repository_and_config_service(ImageSourceRepository)),
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService))
) -> dict:
    image_source_repository, configuration_service = repo_and_config
    entity = RouteHelper.get_entity_with_config_context(
        image_source_repository,
        configuration_service,
        image_source_uid,
        "ImageSource"
    )
    image_source_service.load_settings_to_image_source(uid=image_source_uid)
    model = ImageSourceModel(**entity)
    return model.model_dump()


@router.post("")
@detect_security_threats()
@handle_route_errors("create", "ImageSource", success_status=201)
async def post_image_source(
        image_source: ImageSourceModel,
        user: dict = Depends(require_authentication("create image source")),
        repo_and_config=Depends(get_repository_and_config_service(ImageSourceRepository)),
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService))
) -> Dict[str, str]:
    image_source_repository, configuration_service = repo_and_config
    
    # Create entity in repository
    result = RouteHelper.create_entity_with_config_context(
        image_source_repository,
        configuration_service,
        image_source,
        "ImageSource"
    )
    
    # Initialize the newly created image source in the service cache
    try:
        image_source_service._initialize_image_source_by_uid(image_source.uid)
    except Exception as e:
        print(f"Warning: Failed to initialize image source {image_source.uid} in service cache: {e}")
        # Don't fail the request if cache initialization fails
    
    return result


@router.put("/{image_source_uid}")
@validate_input(image_source_uid="safe_string")
@detect_security_threats()
@handle_route_errors("update", "ImageSource", "image_source_uid")
async def put_image_source(
        image_source: ImageSourceModel,
        user: dict = Depends(require_authentication("update image source")),
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        repo_and_config=Depends(get_repository_and_config_service(ImageSourceRepository))
) -> Dict[str, str]:
    image_source_repository, configuration_service = repo_and_config
    result = RouteHelper.update_entity_with_config_context(
        image_source_repository,
        configuration_service,
        image_source,
        "ImageSource"
    )
    image_source_service.on_patch_image_source(image_source)
    return result


@router.delete("/{image_source_uid}")
@handle_route_errors("delete", "ImageSource", "image_source_uid")
async def delete_image_source(
        image_source_uid: str,
        user: dict = Depends(require_authentication("delete image source")),
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        repo_and_config=Depends(get_repository_and_config_service(ImageSourceRepository))
) -> Dict[str, str]:
    image_source_repository, configuration_service = repo_and_config
    image_source_service.on_delete_image_source(image_source_uid)
    return RouteHelper.delete_entity_with_config_context(
        image_source_repository,
        configuration_service,
        image_source_uid,
        "ImageSource"
    )


manager = ConnectionManager()


@router.websocket("/{image_source_uid}/ws/{ws_uid}")
async def websocket_endpoint(
        websocket: WebSocket,
        ws_uid,
        image_source_uid,
        repo_and_config=Depends(get_repository_and_config_service(ImageSourceRepository)),
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        camera_calibration_service: CameraCalibrationService = Depends(get_service_by_type(CameraCalibrationService))
):
    try:
        await manager.connect(ws_uid, websocket)
        image_source_repository, configuration_service = repo_and_config
        
        # Check if configuration is set before proceeding
        current_config = configuration_service.get_current_configuration_name()
        if not current_config:
            print(f"WebSocket connection attempted without configuration set for image source {image_source_uid}")
            await manager.disconnect(ws_uid)
            return
        
        # Setup configuration context and safely read image source configuration
        try:
            RouteHelper.setup_configuration_context(image_source_repository, configuration_service)
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
                # Check if image source is initialized before trying to grab frames
                if image_source_uid not in image_source_service.image_sources:
                    # Don't spam logs, just wait and check again
                    await sleep(1.0)
                    continue
                    
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
        repo_and_config=Depends(get_repository_and_config_service(ImageSourceRepository)),
        image_source_service: ImageSourceService = Depends(get_service_by_type(ImageSourceService)),
        camera_calibration_service: CameraCalibrationService = Depends(get_service_by_type(CameraCalibrationService))
):
    await manager.connect(ws_uid, websocket)
    image_source_repository, configuration_service = repo_and_config
    RouteHelper.setup_configuration_context(image_source_repository, configuration_service)
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
async def close_ws(ws_uid: str) -> Dict[str, str]:
    try:
        await manager.connection_closed(ws_uid)
        return {"status": "success", "message": "WebSocket connection closed successfully"}
    except Exception as e:
        raise create_error_response("close_ws", "ImageSource", exception=e)
