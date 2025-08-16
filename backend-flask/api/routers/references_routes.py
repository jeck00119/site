from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from starlette import status

from api.dependencies.services import get_service_by_type
from api.error_handlers import handle_route_errors
from api.route_utils import RouteHelper, require_authentication, get_repository_and_config_service
from repo.repositories import ReferencesRepository
from services.references.references_model import ReferenceModel
from services.references.references_service import ReferencesService

router = APIRouter(
    tags=["reference"],
    prefix="/reference"
)


@router.get("")
@handle_route_errors("list", "Reference")
async def list_references(
        _: dict = Depends(require_authentication("list references")),
        repo_and_config=Depends(get_repository_and_config_service(ReferencesRepository))
) -> List[Dict[str, Any]]:
    references_repository, configuration_service = repo_and_config
    references = RouteHelper.list_entities_with_config_context(
        references_repository, configuration_service, "Reference"
    )
    return RouteHelper.transform_list_to_uid_name(references)


@router.get("/{reference_uid}")
@handle_route_errors("retrieve", "Reference", "reference_uid")
async def get_reference(
        reference_uid: str,
        repo_and_config=Depends(get_repository_and_config_service(ReferencesRepository))
) -> ReferenceModel:
    references_repository, configuration_service = repo_and_config
    entity_data = RouteHelper.get_entity_with_config_context(
        references_repository, configuration_service, reference_uid, "Reference"
    )
    return ReferenceModel(**entity_data)


@router.post("")
@handle_route_errors("create", "Reference", success_status=201)
async def post_reference(
        reference: ReferenceModel,
        user: dict = Depends(require_authentication),
        repo_and_config=Depends(get_repository_and_config_service(ReferencesRepository)),
        references_service: ReferencesService = Depends(get_service_by_type(ReferencesService)),
) -> Dict[str, Any]:
    references_repository, configuration_service = repo_and_config
    RouteHelper.create_entity_with_config_context(
        references_repository, configuration_service, reference.model_dump(), "Reference"
    )
    references_service.post_reference(reference)
    return RouteHelper.create_success_response("Reference created successfully", status_code=status.HTTP_201_CREATED)


@router.put("/{reference_uid}")
@handle_route_errors("update", "Reference")
async def put_image_source(
        reference: ReferenceModel,
        user: dict = Depends(require_authentication),
        repo_and_config=Depends(get_repository_and_config_service(ReferencesRepository)),
        references_service: ReferencesService = Depends(get_service_by_type(ReferencesService))
) -> Dict[str, Any]:
    references_repository, configuration_service = repo_and_config
    RouteHelper.update_entity_with_config_context(
        references_repository, configuration_service, reference.model_dump(), "Reference"
    )
    references_service.patch_reference(reference)
    return RouteHelper.create_success_response("Reference updated successfully")


@router.delete("/{reference_uid}")
@handle_route_errors("delete", "Reference", "reference_uid")
async def delete_reference(
        reference_uid: str,
        user: dict = Depends(require_authentication),
        repo_and_config=Depends(get_repository_and_config_service(ReferencesRepository)),
        references_service: ReferencesService = Depends(get_service_by_type(ReferencesService)),
) -> Dict[str, Any]:
    references_repository, configuration_service = repo_and_config
    references_service.delete_reference(reference_uid)
    RouteHelper.delete_entity_with_config_context(
        references_repository, configuration_service, reference_uid, "Reference"
    )
    return RouteHelper.create_success_response("Reference deleted successfully")
