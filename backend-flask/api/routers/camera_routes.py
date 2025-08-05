from asyncio import sleep
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse
from starlette.websockets import WebSocketDisconnect, WebSocket
from wsproto.utilities import LocalProtocolError

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response
from api.route_utils import RouteHelper, require_authentication
from api.ws_connection_manager import ConnectionManager
from repo.repositories import CameraRepository, CameraSettingsRepository
from repo.repository_exceptions import UidNotFound, UidNotUnique
from services.authorization.authorization import get_current_user
from services.camera.camera_model import CameraModel, camera_type_controls, camera_type_default_settings, \
    EnumCameraTypes
from services.camera.camera_service import CameraService
from src.utils import frame_to_base64

router = APIRouter(
    tags=["camera"],
    prefix="/cameras",
)


class Property(BaseModel):
    name: str
    value: Any


@router.get("/camera_types")
async def list_camera_types():
    ret = list(EnumCameraTypes)
    return ret


@router.get("")
async def list_cameras(
        camera_repository: CameraRepository = Depends(get_service_by_type(CameraRepository))
):
    try:
        return RouteHelper.list_entities(camera_repository, "Camera")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="list_cameras",
            entity_type="Camera",
            exception=e
        )


@router.get("/types/{camera_type}")
async def list_cameras_by_type(
        camera_type: str,
        camera_repository: CameraRepository = Depends(get_service_by_type(CameraRepository))
):
    try:
        res = camera_repository.read_all_type(camera_type)
        return res if res else []
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="list_cameras_by_type",
            entity_type="Camera",
            exception=e
        )


@router.get("/controls/{camera_uid}")
async def get_camera_controls(
        camera_uid: str,
        camera_repository: CameraRepository = Depends(get_service_by_type(CameraRepository)),
):
    try:
        camera = RouteHelper.get_entity_by_id(camera_repository, camera_uid, "Camera")
        camera_type = camera['camera_type']
        return camera_type_controls[camera_type]
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="get_camera_controls",
            entity_type="Camera",
            entity_id=camera_uid,
            exception=e
        )


@router.get("/{camera_uid}")
async def get_camera(
        camera_uid: str,
        camera_repository: CameraRepository = Depends(get_service_by_type(CameraRepository)),
):
    try:
        res = RouteHelper.get_entity_by_id(camera_repository, camera_uid, "Camera")
        res_camera_model = CameraModel(**res)
        return {'camera': res_camera_model,
                'controls': camera_type_controls[res_camera_model.camera_type],
                'default_settings': camera_type_default_settings[res_camera_model.camera_type]
                }
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="get_camera",
            entity_type="Camera",
            entity_id=camera_uid,
            exception=e
        )


@router.post("")
async def post_camera(
        camera_model: CameraModel,
        user: dict = Depends(require_authentication("create camera")),
        camera_service: CameraService = Depends(get_service_by_type(CameraService)),
        camera_repository: CameraRepository = Depends(get_service_by_type(CameraRepository))
):
    try:
        camera_repository.create(camera_model)
        camera_service.post_camera(camera_model)
        return RouteHelper.create_success_response("Camera created successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="create_camera",
            entity_type="Camera",
            entity_id=camera_model.uid,
            exception=e
        )


@router.put("/{camera_uid}")
async def put_camera(
        camera_model: CameraModel,
        user: dict = Depends(require_authentication("update camera")),
        camera_service: CameraService = Depends(get_service_by_type(CameraService)),
        camera_repository: CameraRepository = Depends(get_service_by_type(CameraRepository)),
):
    try:
        camera_repository.update(camera_model)
        camera_service.patch_camera(camera_model)
        return RouteHelper.create_success_response("Camera updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="update_camera",
            entity_type="Camera",
            entity_id=camera_model.uid,
            exception=e
        )


@router.delete("/{camera_uid}")
async def delete_camera(
        camera_uid: str,
        user: dict = Depends(require_authentication("delete camera")),
        camera_service: CameraService = Depends(get_service_by_type(CameraService)),
        camera_repository: CameraRepository = Depends(get_service_by_type(CameraRepository)),
):
    try:
        camera_repository.delete(camera_uid)
        camera_service.delete_camera(camera_uid)
        return RouteHelper.create_success_response("Camera deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="delete_camera",
            entity_type="Camera",
            entity_id=camera_uid,
            exception=e
        )


@router.get("/{camera_uid}/settings")
async def get_possible_settings(
        camera_uid: str,
        camera_repository: CameraRepository = Depends(get_service_by_type(CameraRepository)),
        camera_settings_repository: CameraSettingsRepository = Depends(get_service_by_type(CameraSettingsRepository))
):
    try:
        camera_doc = RouteHelper.get_entity_by_id(camera_repository, camera_uid, "Camera")
        res = camera_settings_repository.read_all_by_type(camera_doc['camera_type'])
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="get_camera_settings",
            entity_type="Camera",
            entity_id=camera_uid,
            exception=e
        )


@router.get("/{camera_uid}/settings/{settings_uid}")
async def set_camera_settings(
        camera_uid: str,
        settings_uid: str,
        camera_service: CameraService = Depends(get_service_by_type(CameraService)),
):
    try:
        camera_service.load_setting_file(camera_uid, settings_uid)
        return RouteHelper.create_success_response("Camera settings loaded successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="set_camera_settings",
            entity_type="Camera",
            entity_id=camera_uid,
            exception=e
        )


@router.post("/{camera_uid}/settings")
async def set_camera_settings_from_dict(
        camera_uid: str,
        settings: dict,
        camera_service: CameraService = Depends(get_service_by_type(CameraService))
):
    try:
        camera_service.load_settings_from_dict(camera_uid, settings)
        return RouteHelper.create_success_response("Camera settings applied successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="set_camera_settings_from_dict",
            entity_type="Camera",
            entity_id=camera_uid,
            exception=e
        )


@router.get("/_API_/find_basler_cameras")
async def uninitialized_cameras(
        camera_service: CameraService = Depends(get_service_by_type(CameraService))
):
    try:
        result = camera_service.find_basler_cameras()
        return result if result is not None else RouteHelper.create_success_response("Basler cameras search completed")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="find_basler_cameras",
            entity_type="Camera",
            exception=e
        )


@router.patch("/_API_/{camera_uid}")
async def set_camera_prop(
        camera_uid: str, prop: Property,
        camera_service: CameraService = Depends(get_service_by_type(CameraService)),
):
    try:
        res = camera_service.change_camera_prop(camera_uid, prop.name, prop.value)
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="set_camera_property",
            entity_type="Camera",
            entity_id=camera_uid,
            exception=e
        )


manager = ConnectionManager()


@router.websocket("/{camera_uid}/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        camera_uid: str,
        camera_service: CameraService = Depends(get_service_by_type(CameraService)),
):
    await manager.connect(camera_uid, websocket)
    try:
        while True:
            if manager.is_closed(camera_uid):
                break

            image = frame_to_base64(camera_service.grab_from_camera(camera_uid))
            await websocket.send_bytes(image)
            await sleep(0.05)

        await manager.disconnect(camera_uid)
    except WebSocketDisconnect:
        await manager.disconnect(camera_uid)
    except LocalProtocolError:
        manager.remove_websocket(camera_uid)
    except RuntimeError:
        pass


@router.post("/{camera_uid}/ws/close")
async def close_ws(camera_uid: str):
    try:
        await manager.connection_closed(camera_uid)
        return RouteHelper.create_success_response("WebSocket connection closed successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="close_websocket",
            entity_type="Camera",
            entity_id=camera_uid,
            exception=e
        )
