from typing import List, Dict, Any

from fastapi import APIRouter, Depends
from starlette import status

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response
from api.route_utils import RouteHelper, require_authentication
from repo.repositories import ProfilometerRepository
from repo.repository_exceptions import UidNotFound, UidNotUnique
from services.profilometer.profilometer_models import ProfilometerModel
from services.profilometer.profilometer_service import ProfilometerService

router = APIRouter(
    tags=["profilometer"],
    prefix="/profilometer"
)


@router.get("")
async def get_profilometers(
        profilometer_repository: ProfilometerRepository = Depends(get_service_by_type(ProfilometerRepository)),
) -> List[Dict[str, Any]]:
    try:
        entities = RouteHelper.list_entities(profilometer_repository, "Profilometer")
        return entities
    except Exception as e:
        raise create_error_response(
            operation="list",
            entity_type="Profilometer",
            exception=e
        )


@router.get("/profilometer_types")
async def get_robot_types(
        profilometer_service: ProfilometerService = Depends(get_service_by_type(ProfilometerService))
) -> List[str]:
    try:
        types = profilometer_service.get_available_types()
        return RouteHelper.create_success_response("Types retrieved successfully", types)
    except Exception as e:
        raise create_error_response(
            operation="get_types",
            entity_type="Profilometer",
            exception=e
        )


@router.get("/{profilometer_uid}")
async def get_profilometer(
        profilometer_uid: str,
        profilometer_repository: ProfilometerRepository = Depends(get_service_by_type(ProfilometerRepository)),
) -> ProfilometerModel:
    try:
        entity_data = RouteHelper.get_entity_by_id(profilometer_repository, profilometer_uid, "Profilometer")
        return ProfilometerModel(**entity_data)
    except Exception as e:
        raise create_error_response(
            operation="retrieve",
            entity_type="Profilometer",
            entity_id=profilometer_uid,
            exception=e
        )


@router.post("/save")
async def post_profilometers(
        profilometer_list: List[Dict[str, Any]],
        user: dict = Depends(require_authentication),
        profilometer_repository: ProfilometerRepository = Depends(get_service_by_type(ProfilometerRepository)),
        profilometer_service: ProfilometerService = Depends(get_service_by_type(ProfilometerService))
) -> Dict[str, Any]:
    try:
        profilometer_models = []

        for profilometer in profilometer_list:
            profilometer_models.append(ProfilometerModel(**profilometer))

        add, update, delete = profilometer_service.update_profilometers(profilometer_models)

        for profilometer_model in profilometer_models:
            if profilometer_model.uid in add:
                RouteHelper.create_entity(profilometer_repository, profilometer_model.model_dump(), "Profilometer")
            if profilometer_model.uid in update:
                RouteHelper.update_entity(profilometer_repository, profilometer_model.model_dump(), "Profilometer")
            if profilometer_model.uid in delete:
                RouteHelper.delete_entity(profilometer_repository, profilometer_model.uid, "Profilometer")
        
        return RouteHelper.create_success_response("Profilometers saved successfully")
    except Exception as e:
        raise create_error_response(
            operation="save_batch",
            entity_type="Profilometer",
            exception=e
        )


@router.delete("/{profilometer_uid}")
async def delete_profilometer(
        profilometer_uid: str,
        user: dict = Depends(require_authentication),
        profilometer_repository: ProfilometerRepository = Depends(get_service_by_type(ProfilometerRepository)),
) -> Dict[str, Any]:
    try:
        RouteHelper.delete_entity(profilometer_repository, profilometer_uid, "Profilometer")
        return RouteHelper.create_success_response("Profilometer deleted successfully")
    except Exception as e:
        raise create_error_response(
            operation="delete",
            entity_type="Profilometer",
            entity_id=profilometer_uid,
            exception=e
        )
