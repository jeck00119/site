from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from starlette import status

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response
from api.route_utils import RouteHelper, require_authentication
from repo.repositories import ItacRepository
from repo.repository_exceptions import UidNotFound
from services.itac.itac_model import ItacModel

router = APIRouter(
    tags=["itac"],
    prefix="/itac"
)


@router.get("")
async def get_itac(
        itac_repository: ItacRepository = Depends(get_service_by_type(ItacRepository))
) -> List[Dict[str, Any]]:
    try:
        entities = RouteHelper.list_entities(itac_repository, "ITAC")
        return entities
    except Exception as e:
        raise create_error_response(
            operation="list",
            entity_type="ITAC",
            exception=e
        )


@router.get("/{itac_uid}")
async def get_itac_by_id(
        itac_uid: str,
        itac_repository: ItacRepository = Depends(get_service_by_type(ItacRepository))
) -> ItacModel:
    try:
        entity_data = RouteHelper.get_entity_by_id(itac_repository, itac_uid, "ITAC")
        return ItacModel(**entity_data)
    except Exception as e:
        raise create_error_response(
            operation="retrieve",
            entity_type="ITAC",
            entity_id=itac_uid,
            exception=e
        )


@router.post("")
async def post_itac(
        itac: ItacModel,
        user: dict = Depends(require_authentication),
        itac_repository: ItacRepository = Depends(get_service_by_type(ItacRepository))
) -> Dict[str, Any]:
    try:
        RouteHelper.create_entity(itac_repository, itac, "ITAC")
        return RouteHelper.create_success_response("ITAC created successfully", status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise create_error_response(
            operation="create",
            entity_type="ITAC",
            exception=e
        )


@router.delete("/{itac_uid}")
async def delete_itac(
        itac_uid: str,
        user: dict = Depends(require_authentication),
        itac_repository: ItacRepository = Depends(get_service_by_type(ItacRepository)),
) -> Dict[str, Any]:
    try:
        RouteHelper.delete_entity(itac_repository, itac_uid, "ITAC")
        return RouteHelper.create_success_response("ITAC deleted successfully")
    except Exception as e:
        raise create_error_response(
            operation="delete",
            entity_type="ITAC",
            entity_id=itac_uid,
            exception=e
        )


@router.put("/{itac_uid}")
async def update_itac(
        itac_model: ItacModel,
        user: dict = Depends(require_authentication),
        itac_repository: ItacRepository = Depends(get_service_by_type(ItacRepository)),
) -> Dict[str, Any]:
    try:
        RouteHelper.update_entity(itac_repository, itac_model.model_dump(), "ITAC")
        return RouteHelper.create_success_response("ITAC updated successfully")
    except Exception as e:
        raise create_error_response(
            operation="update",
            entity_type="ITAC",
            entity_id=itac_model.uid if hasattr(itac_model, 'uid') else None,
            exception=e
        )
