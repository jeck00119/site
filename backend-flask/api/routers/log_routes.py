from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies.services import get_service_by_type
from services.logger.logger_model import AppEntry
from services.logger.logger_service import AppLogger

router = APIRouter(
    tags=['log'],
    prefix='/log'
)


@router.get('')
async def get_logs():
    """Get application logs - returns empty array if service unavailable"""
    try:
        # Try to get logger service
        logger_service = AppLogger()
        logs = logger_service.read()
        response_data = logs if logs else []
    except Exception as e:
        # Return empty logs if service is not available
        print(f"Warning: Logger service error: {e}")
        response_data = []
    
    # Create response with explicit CORS headers
    response = JSONResponse(content=response_data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


@router.post('/add')
async def add_log_entry(log_entry: AppEntry):
    """Add log entry - fails silently if service unavailable"""
    try:
        logger_service = AppLogger()
        logger_service.add(log_entry)
        return JSONResponse(status_code=status.HTTP_200_OK, content='')
    except Exception as e:
        print(f"Warning: Failed to add log entry: {e}")
        return JSONResponse(status_code=status.HTTP_200_OK, content='')


@router.delete('/{entry_idx}')
async def remove_entry(
        entry_idx: int,
        logger_service: AppLogger = Depends(get_service_by_type(AppLogger))
):
    logger_service.remove(entry_idx)
    return JSONResponse(status_code=status.HTTP_200_OK, content='')
