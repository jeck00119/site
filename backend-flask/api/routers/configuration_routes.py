from asyncio import sleep

from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.responses import JSONResponse
from starlette.websockets import WebSocketDisconnect, WebSocket
from wsproto.utilities import LocalProtocolError

from api.dependencies.services import get_service_by_type
from api.ws_connection_manager import ConnectionManager
from api.error_handlers import create_error_response
from api.route_utils import RouteHelper, require_authentication
from repo.repositories import ConfigurationRepository
from repo.repository_exceptions import UidNotFound, UidNotUnique
from services.authorization.authorization import get_current_user
from services.configurations.configuration_model import ConfigurationModel
from services.configurations.configurations_service import ConfigurationService

router = APIRouter(
    tags=["configurations"],
    prefix="/configurations"
)

manager = ConnectionManager()


@router.get("")
async def get_configuration(
        _: dict = Depends(require_authentication("list configurations")),
        configuration_repository: ConfigurationRepository = Depends(get_service_by_type(ConfigurationRepository))
):
    return RouteHelper.list_entities(configuration_repository, "Configuration")


@router.get("/current")
async def get_current_configuration(
        _: dict = Depends(require_authentication("get current configuration")),
        configuration_repository: ConfigurationRepository = Depends(get_service_by_type(ConfigurationRepository)),
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
):
    try:
        current_uid = configuration_service.get_current_configuration_uid()
        if not current_uid:
            return None
        configuration = configuration_repository.read_id(current_uid)
        return configuration
    except UidNotFound:
        return None
    except Exception as e:
        raise create_error_response(
            operation="get current configuration",
            entity_type="Configuration Service",
            exception=e
        )


@router.delete("/{configuration_uid}")
async def delete_configuration(
        configuration_uid: str,
        user: dict = Depends(require_authentication("delete configuration")),
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService)),
        configuration_repository: ConfigurationRepository = Depends(get_service_by_type(ConfigurationRepository)),
):
    try:
        configuration_dict = RouteHelper.get_entity_by_id(configuration_repository, configuration_uid, "Configuration")
        configuration_model = ConfigurationModel(**configuration_dict)
        configuration_service.delete_configuration(configuration_model)
        configuration_repository.delete(configuration_uid)
        return RouteHelper.create_success_response(f"Configuration {configuration_uid} deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="delete",
            entity_type="Configuration",
            entity_id=configuration_uid,
            exception=e
        )


@router.post("")
async def post_configuration(
        configuration_model: ConfigurationModel,
        user: dict = Depends(require_authentication("create configuration")),
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService)),
        configuration_repository: ConfigurationRepository = Depends(get_service_by_type(ConfigurationRepository)),
):
    try:
        RouteHelper.create_entity(configuration_repository, configuration_model.model_dump(), "Configuration")
        configuration_service.post_configuration(configuration_model)
        return RouteHelper.create_success_response(
            f"Configuration {configuration_model.name} ({configuration_model.uid}) created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="create",
            entity_type="Configuration",
            entity_id=f"{configuration_model.name} ({configuration_model.uid})",
            exception=e
        )


@router.post("/copy/{original_configuration_uid}")
async def copy_configuration(
        original_configuration_uid: str,
        configuration_model: ConfigurationModel,
        user: dict = Depends(require_authentication("copy configuration")),
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService)),
        configuration_repository: ConfigurationRepository = Depends(get_service_by_type(ConfigurationRepository)),
):
    try:
        RouteHelper.create_entity(configuration_repository, configuration_model.model_dump(), "Configuration")
        configuration_service.copy_configuration(configuration_model, original_configuration_uid)
        return RouteHelper.create_success_response(
            f"Configuration copied from {original_configuration_uid} to {configuration_model.name} ({configuration_model.uid})",
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="copy",
            entity_type="Configuration",
            entity_id=f"from {original_configuration_uid} to {configuration_model.name} ({configuration_model.uid})",
            exception=e
        )


@router.put("/{configuration_uid}")
async def put_configuration(
        configuration_uid: str,
        new_configuration_model: ConfigurationModel,
        user: dict = Depends(require_authentication("update configuration")),
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService)),
        configuration_repository: ConfigurationRepository = Depends(get_service_by_type(ConfigurationRepository))
):
    try:
        old_configuration_dict = RouteHelper.get_entity_by_id(configuration_repository, configuration_uid, "Configuration")
        old_configuration_model = ConfigurationModel(**old_configuration_dict)

        # Ensure UID matches
        new_configuration_model.uid = configuration_uid
        RouteHelper.update_entity(configuration_repository, new_configuration_model.model_dump(), "Configuration")

        current_config_uid = configuration_service.get_current_configuration_uid()

        if current_config_uid == configuration_uid:
            # if current configuration is in use, need to reset all databases [Access Denied - Windows Error]
            configuration_service.reset_dbs()
            configuration_service.update_configuration(old_configuration_model, new_configuration_model)

            # set new path in the databases
            configuration_service.load_configuration(configuration_uid=configuration_uid)
        else:
            configuration_service.update_configuration(old_configuration_model, new_configuration_model)
        
        return RouteHelper.create_success_response(f"Configuration {configuration_uid} updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="update",
            entity_type="Configuration",
            entity_id=configuration_uid,
            exception=e
        )


@router.get("/{configuration_uid}")
async def load_configuration(
        configuration_uid: str,
        _: dict = Depends(require_authentication("load configuration")),
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
):
    try:
        configuration_service.load_configuration(configuration_uid=configuration_uid)
        return RouteHelper.create_success_response(f"Configuration {configuration_uid} loaded successfully")
    except UidNotFound:
        raise create_error_response(
            operation="load",
            entity_type="Configuration",
            entity_id=configuration_uid,
            exception=UidNotFound("Configuration not found")
        )
    except Exception as e:
        raise create_error_response(
            operation="load",
            entity_type="Configuration",
            entity_id=configuration_uid,
            exception=e
        )


@router.post("/reset_all_dbs")
async def reset_all_dbs(
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
):
    try:
        configuration_service.reset_dbs()
        return RouteHelper.create_success_response("All databases reset successfully")
    except Exception as e:
        raise create_error_response(
            operation="reset all databases",
            entity_type="Configuration Service",
            exception=e
        )


@router.websocket("/configuration_changes/{ws_uid}/ws")
async def send_communication_changes(
        ws_uid: str,
        websocket: WebSocket,
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService)),
        configuration_repository: ConfigurationRepository = Depends(get_service_by_type(ConfigurationRepository))
):
    await manager.connect(ws_uid, websocket)
    try:
        while True:
            if manager.is_closed(ws_uid):
                break

            if configuration_service.get_configuration_flag_socket():
                configuration = configuration_repository.read_id(configuration_service.get_current_configuration_uid())
                ret = {'configuration': configuration}
                configuration_service.reset_configuration_flag_socket()
                await websocket.send_json(ret)
            
            # Use centralized sleep with cancellation handling
            if not await manager.safe_sleep_with_cancellation(0.3):
                break  # Cancelled, exit loop

        await manager.disconnect(ws_uid)
    except WebSocketDisconnect:
        await manager.disconnect(ws_uid)
    except LocalProtocolError:
        manager.remove_websocket(ws_uid)
    except asyncio.CancelledError:
        # Handle cancellation during shutdown
        manager.remove_websocket(ws_uid)


@router.post("/{ws_uid}/ws/close")
async def close_configuration_changes_ws(ws_uid: str):
    await manager.connection_closed(ws_uid)
    return JSONResponse(status_code=status.HTTP_200_OK, content='')
