from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from starlette import status

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response
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
async def list_components(
        custom_components_repository: CustomComponentsRepository
        = Depends(get_service_by_type(CustomComponentsRepository))
) -> List[Dict[str, Any]]:
    try:
        components = RouteHelper.list_entities(custom_components_repository, "CustomComponent")
        return RouteHelper.transform_list_to_uid_name(components)
    except Exception as e:
        raise create_error_response(
            operation="list",
            entity_type="CustomComponent",
            exception=e
        )


@router.get('/{custom_component_uid}')
async def get_component(
        custom_component_uid: str,
        custom_components_repository: CustomComponentsRepository = Depends(
            get_service_by_type(CustomComponentsRepository))
) -> CustomComponentModel:
    try:
        entity_data = RouteHelper.get_entity_by_id(custom_components_repository, custom_component_uid, "CustomComponent")
        return CustomComponentModel(**entity_data)
    except Exception as e:
        raise create_error_response(
            operation="retrieve",
            entity_type="CustomComponent",
            entity_id=custom_component_uid,
            exception=e
        )


@router.post('')
async def post_component(
        custom_component: CustomComponentModel,
        user: dict = Depends(require_authentication),
        custom_components_repository: CustomComponentsRepository = Depends(
            get_service_by_type(CustomComponentsRepository)),
        custom_components_service: CustomComponentsService = Depends(
            get_service_by_type(CustomComponentsService))
) -> Dict[str, Any]:
    try:
        RouteHelper.create_entity(custom_components_repository, custom_component.model_dump(), "CustomComponent")
        custom_components_service.post_component(custom_component)
        return RouteHelper.create_success_response("CustomComponent created successfully", status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise create_error_response(
            operation="create",
            entity_type="CustomComponent",
            exception=e
        )


@router.put('/{custom_component_uid}')
async def update_component(
        custom_component: CustomComponentModel,
        user: dict = Depends(require_authentication),
        custom_components_repository: CustomComponentsRepository = Depends(
            get_service_by_type(CustomComponentsRepository)),
        custom_components_service: CustomComponentsService = Depends(
            get_service_by_type(CustomComponentsService))
) -> Dict[str, Any]:
    try:
        RouteHelper.update_entity(custom_components_repository, custom_component.model_dump(), "CustomComponent")
        custom_components_service.patch_component(custom_component)
        return RouteHelper.create_success_response("CustomComponent updated successfully")
    except Exception as e:
        raise create_error_response(
            operation="update",
            entity_type="CustomComponent",
            entity_id=custom_component.uid if hasattr(custom_component, 'uid') else None,
            exception=e
        )


@router.delete('/{custom_component_uid}')
async def delete_component(
        custom_component_uid: str,
        user: dict = Depends(require_authentication),
        custom_components_repository: CustomComponentsRepository = Depends(
            get_service_by_type(CustomComponentsRepository)),
        custom_components_service: CustomComponentsService = Depends(
            get_service_by_type(CustomComponentsService))
) -> Dict[str, Any]:
    try:
        custom_components_service.delete_component(custom_component_uid)
        RouteHelper.delete_entity(custom_components_repository, custom_component_uid, "CustomComponent")
        return RouteHelper.create_success_response("CustomComponent deleted successfully")
    except Exception as e:
        raise create_error_response(
            operation="delete",
            entity_type="CustomComponent",
            entity_id=custom_component_uid,
            exception=e
        )


@router.get('/__API__/process_live_component/{image_source_uid}')
async def process_component(
        image_source_uid: str,
        custom_components_service: CustomComponentsService = Depends(
            get_service_by_type(CustomComponentsService))
) -> Dict[str, Any]:
    try:
        out_image, results = custom_components_service.process_live_component(image_source_uid)
        response_data = {
            'frame': frame_to_base64(out_image),
            'results': results,
            'data': ''
        }
        return RouteHelper.create_success_response(response_data)
    except Exception as e:
        raise create_error_response(
            operation="process_live",
            entity_type="CustomComponent",
            entity_id=image_source_uid,
            exception=e
        )
