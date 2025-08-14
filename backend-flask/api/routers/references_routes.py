from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from starlette import status

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response
from api.route_utils import RouteHelper, require_authentication
from repo.repositories import ReferencesRepository
from repo.repository_exceptions import UidNotFound
from services.references.references_model import ReferenceModel
from services.references.references_service import ReferencesService
from services.configurations.configurations_service import ConfigurationService

router = APIRouter(
    tags=["reference"],
    prefix="/reference"
)


@router.get("")
async def list_references(
        references_repository: ReferencesRepository = Depends(get_service_by_type(ReferencesRepository)),
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
) -> List[Dict[str, Any]]:
    try:
        # Ensure repository has correct configuration context
        current_config = configuration_service.get_current_configuration_name()
        if current_config:
            references_repository.set_db(current_config)
        
        references = RouteHelper.list_entities(references_repository, "Reference")
        return RouteHelper.transform_list_to_uid_name(references)
    except Exception as e:
        raise create_error_response(
            operation="list",
            entity_type="Reference",
            exception=e
        )


@router.get("/{reference_uid}")
async def get_reference(
        reference_uid: str,
        references_repository: ReferencesRepository = Depends(get_service_by_type(ReferencesRepository)),
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
) -> ReferenceModel:
    try:
        # Ensure repository has correct configuration context
        current_config = configuration_service.get_current_configuration_name()
        if current_config:
            references_repository.set_db(current_config)
            
        entity_data = RouteHelper.get_entity_by_id(references_repository, reference_uid, "Reference")
        return ReferenceModel(**entity_data)
    except Exception as e:
        raise create_error_response(
            operation="get",
            entity_type="Reference",
            entity_id=reference_uid,
            exception=e
        )


@router.post("")
async def post_reference(
        reference: ReferenceModel,
        user: dict = Depends(require_authentication),
        references_repository: ReferencesRepository = Depends(get_service_by_type(ReferencesRepository)),
        references_service: ReferencesService = Depends(get_service_by_type(ReferencesService)),
) -> Dict[str, Any]:
    try:
        RouteHelper.create_entity(references_repository, reference.model_dump(), "Reference")
        references_service.post_reference(reference)
        return RouteHelper.create_success_response("Reference created successfully", status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise create_error_response(
            operation="create",
            entity_type="Reference",
            exception=e
        )


@router.put("/{reference_uid}")
async def put_image_source(
        reference: ReferenceModel,
        user: dict = Depends(require_authentication),
        references_repository: ReferencesRepository = Depends(get_service_by_type(ReferencesRepository)),
        references_service: ReferencesService = Depends(get_service_by_type(ReferencesService))
) -> Dict[str, Any]:
    try:
        RouteHelper.update_entity(references_repository, reference.model_dump(), "Reference")
        references_service.patch_reference(reference)
        return RouteHelper.create_success_response("Reference updated successfully")
    except Exception as e:
        raise create_error_response(
            operation="update",
            entity_type="Reference",
            entity_id=reference.uid if hasattr(reference, 'uid') else None,
            exception=e
        )


@router.delete("/{reference_uid}")
async def delete_reference(
        reference_uid: str,
        user: dict = Depends(require_authentication),
        references_repository: ReferencesRepository = Depends(get_service_by_type(ReferencesRepository)),
        references_service: ReferencesService = Depends(get_service_by_type(ReferencesService)),
) -> Dict[str, Any]:
    try:
        references_service.delete_reference(reference_uid)
        RouteHelper.delete_entity(references_repository, reference_uid, "Reference")
        return RouteHelper.create_success_response("Reference deleted successfully")
    except Exception as e:
        raise create_error_response(
            operation="delete",
            entity_type="Reference",
            entity_id=reference_uid,
            exception=e
        )
