from typing import Dict, List
from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response
from api.route_utils import RouteHelper, require_authentication
from security.validators import validate_input, detect_security_threats
from repo.repositories import ComponentsRepository, AlgorithmsRepository
from repo.repository_exceptions import UidNotFound
from services.authorization.authorization import get_current_user
from services.components.components_model import ComponentModel
from services.components.components_service import ComponentsService

router = APIRouter(
    tags=["component"],
    prefix="/component"
)


@router.get("")
async def list_components(
        components_repository: ComponentsRepository = Depends(get_service_by_type(ComponentsRepository)),
) -> List[Dict[str, str]]:
    try:
        components = RouteHelper.list_entities(components_repository, "Component")
        return RouteHelper.transform_list_to_uid_name(components)
    except Exception as e:
        raise create_error_response(
            operation="list",
            entity_type="Component",
            exception=e
        )


@router.get("/{component_uid}")
@validate_input(component_uid="safe_string")
async def get_component(
        component_uid: str,
        components_repository: ComponentsRepository = Depends(get_service_by_type(ComponentsRepository)),
        algorithms_repo: AlgorithmsRepository = Depends(get_service_by_type(AlgorithmsRepository)),
) -> ComponentModel:
    try:
        res = RouteHelper.get_entity_by_id(
            components_repository,
            component_uid,
            "Component"
        )
        component = ComponentModel(**res)
        if component.algorithm_uid:
            component.algorithm_type = algorithms_repo.get_type_from_uid(component.algorithm_uid)
        return component
    except Exception as e:
        raise create_error_response("retrieve", "Component", component_uid, e)


@router.post("")
@detect_security_threats()
async def post_component(
        component: ComponentModel,
        _: dict = Depends(require_authentication("create component")),
        components_repository: ComponentsRepository = Depends(get_service_by_type(ComponentsRepository)),
        components_service: ComponentsService = Depends(get_service_by_type(ComponentsService)),
) -> Dict[str, str]:
    try:
        result = RouteHelper.create_entity(
            components_repository,
            component,
            "Component"
        )
        components_service.post_component(component)
        return result
    except Exception as e:
        raise create_error_response("create", "Component", exception=e)


@router.put("/{component_uid}")
@validate_input(component_uid="safe_string")
@detect_security_threats()
async def put_component(
        component_uid: str,
        component: ComponentModel,
        _: dict = Depends(require_authentication("update component")),
        components_repository: ComponentsRepository = Depends(get_service_by_type(ComponentsRepository)),
        components_service: ComponentsService = Depends(get_service_by_type(ComponentsService)),
) -> Dict[str, str]:
    try:
        result = RouteHelper.update_entity(
            components_repository,
            component,
            "Component"
        )
        components_service.patch_component(component)
        return result
    except Exception as e:
        raise create_error_response("update", "Component", component_uid, e)


@router.delete("/{component_uid}")
@validate_input(component_uid="safe_string")
async def delete_component(
        component_uid: str,
        _: dict = Depends(require_authentication("delete component")),
        components_repository: ComponentsRepository = Depends(get_service_by_type(ComponentsRepository)),
        components_service: ComponentsService = Depends(get_service_by_type(ComponentsService)),
) -> Dict[str, str]:
    try:
        components_service.delete_component(component_uid)
        return RouteHelper.delete_entity(
            components_repository,
            component_uid,
            "Component"
        )
    except Exception as e:
        raise create_error_response("delete", "Component", component_uid, e)
