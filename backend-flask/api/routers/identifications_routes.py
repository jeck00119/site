from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from starlette import status

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response
from api.route_utils import RouteHelper, require_authentication
from repo.repositories import IdentificationsRepository
from repo.repository_exceptions import UidNotFound
from services.identifications.identifications_model import IdentificationModel

router = APIRouter(
    tags=["identification"],
    prefix="/identification"
)


@router.get("")
async def list_identifications(
        identifications_repository: IdentificationsRepository = Depends(get_service_by_type(IdentificationsRepository)),
) -> List[Dict[str, Any]]:
    try:
        identifications = RouteHelper.list_entities(identifications_repository, "Identification")
        return RouteHelper.transform_list_to_uid_name(identifications)
    except Exception as e:
        raise create_error_response(
            operation="list",
            entity_type="Identification",
            exception=e
        )


@router.get("/{identification_uid}")
async def get_identification(
        identification_uid: str,
        identifications_repository: IdentificationsRepository = Depends(get_service_by_type(IdentificationsRepository)),
) -> IdentificationModel:
    try:
        entity_data = RouteHelper.get_entity_by_id(identifications_repository, identification_uid, "Identification")
        return IdentificationModel(**entity_data)
    except Exception as e:
        raise create_error_response(
            operation="retrieve",
            entity_type="Identification",
            entity_id=identification_uid,
            exception=e
        )


@router.post("")
async def post_identification(
        identification: IdentificationModel,
        user: dict = Depends(require_authentication),
        identifications_repository: IdentificationsRepository = Depends(get_service_by_type(IdentificationsRepository))
) -> Dict[str, Any]:
    try:
        RouteHelper.create_entity(identifications_repository, identification.model_dump(), "Identification")
        return RouteHelper.create_success_response("Identification created successfully", status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise create_error_response(
            operation="create",
            entity_type="Identification",
            exception=e
        )


@router.put("/{identification_uid}")
async def put_image_source(
        identification: IdentificationModel,
        user: dict = Depends(require_authentication),
        identifications_repository: IdentificationsRepository = Depends(get_service_by_type(IdentificationsRepository))
) -> Dict[str, Any]:
    try:
        RouteHelper.update_entity(identifications_repository, identification.model_dump(), "Identification")
        return RouteHelper.create_success_response("Identification updated successfully")
    except Exception as e:
        raise create_error_response(
            operation="update",
            entity_type="Identification",
            entity_id=identification.uid if hasattr(identification, 'uid') else None,
            exception=e
        )


@router.delete("/{identification_uid}")
async def delete_identification(
        identification_uid: str,
        user: dict = Depends(require_authentication),
        identifications_repository: IdentificationsRepository = Depends(get_service_by_type(IdentificationsRepository))
) -> Dict[str, Any]:
    try:
        RouteHelper.delete_entity(identifications_repository, identification_uid, "Identification")
        return RouteHelper.create_success_response("Identification deleted successfully")
    except Exception as e:
        raise create_error_response(
            operation="delete",
            entity_type="Identification",
            entity_id=identification_uid,
            exception=e
        )
