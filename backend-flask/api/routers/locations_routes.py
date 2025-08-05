from typing import Dict, List
from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.responses import JSONResponse

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response
from api.route_utils import RouteHelper, require_authentication
from repo.repositories import LocationRepository
from repo.repository_exceptions import UidNotFound, UidNotUnique
from services.authorization.authorization import get_current_user
from services.cnc.cnc_models import LocationModel

router = APIRouter(
    tags=["location"],
    prefix="/location"
)


@router.get("")
async def get_locations(
        location_repository: LocationRepository = Depends(get_service_by_type(LocationRepository)),
) -> List[Dict]:
    try:
        return RouteHelper.list_entities(
            location_repository,
            "Location"
        )
    except Exception as e:
        raise create_error_response("list", "Location", exception=e)


@router.get("/axis/{axis_uid}")
async def get_locations_by_axis(
        axis_uid: str,
        location_repository: LocationRepository = Depends(get_service_by_type(LocationRepository)),
) -> List[Dict]:
    try:
        return location_repository.get_locations_by_axis_uid(axis_uid)
    except Exception as e:
        raise create_error_response("retrieve", "Location", axis_uid, e)


@router.get("/{location_uid}")
async def get_location(
        location_uid: str,
        location_repository: LocationRepository = Depends(get_service_by_type(LocationRepository)),
) -> LocationModel:
    try:
        res = RouteHelper.get_entity_by_id(
            location_repository,
            location_uid,
            "Location"
        )
        return LocationModel(**res)
    except Exception as e:
        raise create_error_response("retrieve", "Location", location_uid, e)


@router.post("")
async def post_location(
        location_model: LocationModel,
        _: dict = Depends(require_authentication("create location")),
        location_repository: LocationRepository = Depends(get_service_by_type(LocationRepository)),
) -> Dict[str, str]:
    try:
        return RouteHelper.create_entity(
            location_repository,
            location_model,
            "Location"
        )
    except Exception as e:
        raise create_error_response("create", "Location", exception=e)


@router.put("/{location_uid}")
async def put_location(
        location_uid: str,
        location_model: LocationModel,
        _: dict = Depends(require_authentication("update location")),
        location_repository: LocationRepository = Depends(get_service_by_type(LocationRepository)),
) -> Dict[str, str]:
    try:
        return RouteHelper.update_entity(
            location_repository,
            location_model,
            "Location"
        )
    except Exception as e:
        raise create_error_response("update", "Location", location_uid, e)


@router.delete("/{location_uid}")
async def delete_location(
        location_uid: str,
        _: dict = Depends(require_authentication("delete location")),
        location_repository: LocationRepository = Depends(get_service_by_type(LocationRepository)),
) -> Dict[str, str]:
    try:
        return RouteHelper.delete_entity(
            location_repository,
            location_uid,
            "Location"
        )
    except Exception as e:
        raise create_error_response("delete", "Location", location_uid, e)
