from typing import Union

from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.responses import JSONResponse

from api.dependencies.services import get_service_by_type
from api.error_handlers import handle_route_errors, validate_authentication
from repo.repositories import CameraSettingsRepository
from repo.repository_exceptions import UidNotFound, UidNotUnique
from services.authorization.authorization import get_current_user
from services.camera.camera_model import WebCamSettingsModel, BaslerSettingsModel

router = APIRouter(
    tags=["camera_settings"],
    prefix="/camera_settings"
)


@router.get("")
@handle_route_errors("list", "CameraSetting")
async def list_camera_settings(
        camera_settings_repo: CameraSettingsRepository = Depends(get_service_by_type(CameraSettingsRepository))
):
    ret = []
    for cam_set in camera_settings_repo.read_all():
        ret.append(
            {'uid': cam_set['uid'],
             'name': cam_set['name']})
    return ret


@router.get("/{settings_uid}")
@handle_route_errors("retrieve", "CameraSetting", "settings_uid")
async def get_camera_settings(
        settings_uid,
        camera_settings_repository: CameraSettingsRepository = Depends(get_service_by_type(CameraSettingsRepository))
):
    # Todo factory to get good model from doc
    res = camera_settings_repository.read_id(settings_uid)
    return res


@router.post("")
@handle_route_errors("create", "CameraSetting", success_status=status.HTTP_201_CREATED)
async def post_camera_settings(
        settings_model: Union[WebCamSettingsModel, BaslerSettingsModel],
        user: dict = Depends(get_current_user),
        camera_settings_repo: CameraSettingsRepository = Depends(get_service_by_type(CameraSettingsRepository))
):
    validate_authentication(user, "create camera settings")
    camera_settings_repo.create(settings_model)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content='')


@router.put("/{settings_uid}")
@handle_route_errors("update", "CameraSetting", "settings_uid")
async def put_camera_settings(
        settings_model: Union[WebCamSettingsModel, BaslerSettingsModel],
        user: dict = Depends(get_current_user),
        camera_settings_repo: CameraSettingsRepository = Depends(get_service_by_type(CameraSettingsRepository))
):
    validate_authentication(user, "update camera settings")
    camera_settings_repo.update(settings_model)
    return JSONResponse(status_code=status.HTTP_200_OK, content='')


@router.delete("/{settings_uid}")
@handle_route_errors("delete", "CameraSetting", "settings_uid")
async def delete_camera_settings(
        settings_uid,
        user: dict = Depends(get_current_user),
        camera_settings_repo: CameraSettingsRepository = Depends(get_service_by_type(CameraSettingsRepository))
):
    validate_authentication(user, "delete camera settings")
    camera_settings_repo.delete(settings_uid)
    return JSONResponse(status_code=status.HTTP_200_OK, content='')


@router.get("/type/{settings_type}")
@handle_route_errors("retrieve", "CameraSetting type", "settings_type")
async def list_camera_settings_type(
        settings_type,
        camera_settings_repo: CameraSettingsRepository = Depends(get_service_by_type(CameraSettingsRepository))
):
    return camera_settings_repo.read_id(settings_type)
