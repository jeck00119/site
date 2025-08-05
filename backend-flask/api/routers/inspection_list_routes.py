from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response
from api.route_utils import RouteHelper, require_authentication
from repo.repositories import InspectionsRepository
from services.interpreter.inspection_model import InspectionsModel

router = APIRouter(
    tags=["inspection_list"],
    prefix="/inspection_list"
)


@router.get("")
async def get_inspection_list(
        inspection_list_repository: InspectionsRepository = Depends(get_service_by_type(InspectionsRepository))
) -> Dict[str, Any]:
    """
    Get inspection list. Returns empty object if no configuration is loaded
    to prevent frontend crashes.
    """
    try:
        inspection_list = inspection_list_repository.get()
        # Ensure we return a proper data structure instead of None/null
        if inspection_list is None:
            inspection_list = {}  # Return empty object if no data
        return inspection_list
    except:
        # Always return empty object on any error to prevent frontend crashes
        # This handles cases where no configuration is selected or other errors
        return {}


@router.post("")
async def post_inspection_list(
        inspection_list: InspectionsModel,
        user: dict = Depends(require_authentication),
        inspection_list_repository: InspectionsRepository = Depends(get_service_by_type(InspectionsRepository))
) -> JSONResponse:
    try:
        inspection_list_repository.update(inspection_list)
        return RouteHelper.create_success_response("Inspection list updated successfully")
    except Exception as e:
        raise create_error_response(
            operation="update",
            entity_type="InspectionList",
            exception=e
        )
