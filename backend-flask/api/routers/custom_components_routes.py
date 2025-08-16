from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from starlette import status

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response, handle_route_errors
from api.route_utils import RouteHelper, require_authentication
from repo.repositories import CustomComponentsRepository
from repo.repository_exceptions import UidNotFound
from services.custom_components.custom_components_model import CustomComponentModel
from services.custom_components.custom_components_service import CustomComponentsService
from services.services_exceptions import NoLiveAlgSet, NoLiveFrameSet
from src.utils import frame_to_base64

router = APIRouter(
    tags=["custom_component"],
    prefix="/custom_component"
)


@router.get('')
@handle_route_errors("list", "CustomComponent")
async def list_components(
        custom_components_repository: CustomComponentsRepository
        = Depends(get_service_by_type(CustomComponentsRepository))
) -> List[Dict[str, Any]]:
    components = RouteHelper.list_entities(custom_components_repository, "CustomComponent")
    return RouteHelper.transform_list_to_uid_name(components)


@router.get('/{custom_component_uid}')
@handle_route_errors("retrieve", "CustomComponent", "custom_component_uid")
async def get_component(
        custom_component_uid: str,
        custom_components_repository: CustomComponentsRepository = Depends(
            get_service_by_type(CustomComponentsRepository))
) -> CustomComponentModel:
    entity_data = RouteHelper.get_entity_by_id(custom_components_repository, custom_component_uid, "CustomComponent")
    return CustomComponentModel(**entity_data)


@router.post('')
@handle_route_errors("create", "CustomComponent", success_status=201)
async def post_component(
        custom_component: CustomComponentModel,
        user: dict = Depends(require_authentication),
        custom_components_repository: CustomComponentsRepository = Depends(
            get_service_by_type(CustomComponentsRepository)),
        custom_components_service: CustomComponentsService = Depends(
            get_service_by_type(CustomComponentsService))
) -> Dict[str, Any]:
    RouteHelper.create_entity(custom_components_repository, custom_component.model_dump(), "CustomComponent")
    custom_components_service.post_component(custom_component)
    return RouteHelper.create_success_response("CustomComponent created successfully", status_code=status.HTTP_201_CREATED)


@router.put('/{custom_component_uid}')
@handle_route_errors("update", "CustomComponent")
async def update_component(
        custom_component: CustomComponentModel,
        user: dict = Depends(require_authentication),
        custom_components_repository: CustomComponentsRepository = Depends(
            get_service_by_type(CustomComponentsRepository)),
        custom_components_service: CustomComponentsService = Depends(
            get_service_by_type(CustomComponentsService))
) -> Dict[str, Any]:
    RouteHelper.update_entity(custom_components_repository, custom_component.model_dump(), "CustomComponent")
    custom_components_service.patch_component(custom_component)
    return RouteHelper.create_success_response("CustomComponent updated successfully")


@router.delete('/{custom_component_uid}')
@handle_route_errors("delete", "CustomComponent", "custom_component_uid")
async def delete_component(
        custom_component_uid: str,
        user: dict = Depends(require_authentication),
        custom_components_repository: CustomComponentsRepository = Depends(
            get_service_by_type(CustomComponentsRepository)),
        custom_components_service: CustomComponentsService = Depends(
            get_service_by_type(CustomComponentsService))
) -> Dict[str, Any]:
    custom_components_service.delete_component(custom_component_uid)
    RouteHelper.delete_entity(custom_components_repository, custom_component_uid, "CustomComponent")
    return RouteHelper.create_success_response("CustomComponent deleted successfully")


@router.get('/__API__/process_live_component/{image_source_uid}')
@handle_route_errors("process_live", "CustomComponent", "image_source_uid")
async def process_component(
        image_source_uid: str,
        custom_components_service: CustomComponentsService = Depends(
            get_service_by_type(CustomComponentsService))
) -> Dict[str, Any]:
    out_image, results = custom_components_service.process_live_component(image_source_uid)
    response_data = {
        'frame': frame_to_base64(out_image),
        'results': results,
        'data': ''
    }
    return RouteHelper.create_success_response("Component processed successfully", response_data)
