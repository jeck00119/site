from typing import Dict, List
from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.responses import JSONResponse

from api.error_handlers import handle_route_errors
from api.route_utils import RouteHelper, require_authentication, get_repository_and_config_service
from repo.repositories import LocationRepository
from services.cnc.cnc_models import LocationModel

router = APIRouter(
    tags=["location"],
    prefix="/location"
)


@router.get("")
@handle_route_errors("list", "Location")
async def get_locations(
        repo_and_config=Depends(get_repository_and_config_service(LocationRepository))
) -> List[Dict]:
    location_repository, configuration_service = repo_and_config
    return RouteHelper.list_entities_with_config_context(
        location_repository, configuration_service, "Location"
    )


@router.get("/axis/{axis_uid}")
@handle_route_errors("retrieve", "Location", "axis_uid")
async def get_locations_by_axis(
        axis_uid: str,
        repo_and_config=Depends(get_repository_and_config_service(LocationRepository))
) -> List[Dict]:
    location_repository, configuration_service = repo_and_config
    RouteHelper.setup_configuration_context(location_repository, configuration_service)
    return location_repository.get_locations_by_axis_uid(axis_uid)


@router.get("/{location_uid}")
@handle_route_errors("retrieve", "Location", "location_uid")
async def get_location(
        location_uid: str,
        repo_and_config=Depends(get_repository_and_config_service(LocationRepository))
) -> LocationModel:
    location_repository, configuration_service = repo_and_config
    res = RouteHelper.get_entity_with_config_context(
        location_repository, configuration_service, location_uid, "Location"
    )
    return LocationModel(**res)


@router.post("")
@handle_route_errors("create", "Location", success_status=201)
async def post_location(
        location_model: LocationModel,
        _: dict = Depends(require_authentication("create location")),
        repo_and_config=Depends(get_repository_and_config_service(LocationRepository))
) -> Dict[str, str]:
    location_repository, configuration_service = repo_and_config
    return RouteHelper.create_entity_with_config_context(
        location_repository, configuration_service, location_model, "Location"
    )


@router.put("/{location_uid}")
@handle_route_errors("update", "Location", "location_uid")
async def put_location(
        location_uid: str,
        location_model: LocationModel,
        _: dict = Depends(require_authentication("update location")),
        repo_and_config=Depends(get_repository_and_config_service(LocationRepository))
) -> Dict[str, str]:
    location_repository, configuration_service = repo_and_config
    return RouteHelper.update_entity_with_config_context(
        location_repository, configuration_service, location_model, "Location"
    )


@router.delete("/{location_uid}")
@handle_route_errors("delete", "Location", "location_uid")
async def delete_location(
        location_uid: str,
        _: dict = Depends(require_authentication("delete location")),
        repo_and_config=Depends(get_repository_and_config_service(LocationRepository))
) -> Dict[str, str]:
    location_repository, configuration_service = repo_and_config
    return RouteHelper.delete_entity_with_config_context(
        location_repository, configuration_service, location_uid, "Location"
    )
