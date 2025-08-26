import os
import logging
from typing import List
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from starlette import status
from starlette.responses import JSONResponse

from api.dependencies.services import get_service_by_type
from api.error_handlers import handle_route_errors, validate_authentication
from services.authorization.authorization import get_current_user
from services.image_stitching.image_stitching_service import ImageStitchingService
from services.image_stitching.image_stitching_models import (
    ImageStitchingConfigModel,
    StitchingSessionModel,
    StitchingProgressModel,
    StitchingResultModel,
    CapturePositionModel
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["image_stitching"],
    prefix="/image_stitching",
)


@router.post("/session", response_model=StitchingSessionModel)
@handle_route_errors("create", "image stitching session")
async def create_stitching_session(
    config: ImageStitchingConfigModel,
    user: dict = Depends(get_current_user),
    stitching_service: ImageStitchingService = Depends(get_service_by_type(ImageStitchingService))
):
    """Create a new image stitching session with the given configuration."""
    validate_authentication(user, "create image stitching session")
    
    try:
        session = stitching_service.create_stitching_session(config)
        logger.info(f"Created stitching session {session.uid} for user {user.get('email', 'unknown')}")
        return session
    except Exception as e:
        logger.error(f"Failed to create stitching session: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create stitching session: {str(e)}"
        )


@router.get("/session/{session_uid}", response_model=StitchingSessionModel)
@handle_route_errors("get", "image stitching session")
async def get_stitching_session(
    session_uid: str,
    user: dict = Depends(get_current_user),
    stitching_service: ImageStitchingService = Depends(get_service_by_type(ImageStitchingService))
):
    """Get stitching session by UID."""
    validate_authentication(user, "get image stitching session")
    
    try:
        session = stitching_service.get_session(session_uid)
        return session
    except Exception as e:
        logger.error(f"Failed to get stitching session {session_uid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {str(e)}"
        )


@router.get("/session/{session_uid}/progress", response_model=StitchingProgressModel)
@handle_route_errors("get", "stitching progress")
async def get_stitching_progress(
    session_uid: str,
    user: dict = Depends(get_current_user),
    stitching_service: ImageStitchingService = Depends(get_service_by_type(ImageStitchingService))
):
    """Get progress information for a stitching session."""
    validate_authentication(user, "get stitching progress")
    
    try:
        progress = stitching_service.get_session_progress(session_uid)
        return progress
    except Exception as e:
        logger.error(f"Failed to get progress for session {session_uid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {str(e)}"
        )


@router.post("/session/{session_uid}/capture")
@handle_route_errors("capture", "image at position")
async def capture_image_at_position(
    session_uid: str,
    position: CapturePositionModel,
    user: dict = Depends(get_current_user),
    stitching_service: ImageStitchingService = Depends(get_service_by_type(ImageStitchingService))
):
    """Capture image at the specified position."""
    validate_authentication(user, "capture image for stitching")
    
    try:
        captured_image = stitching_service.capture_image_at_position(session_uid, position)
        logger.debug(f"Captured image at position ({position.x}, {position.y}) for session {session_uid}")
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "captured_image_uid": captured_image.uid,
                "position": {
                    "x": captured_image.position.x,
                    "y": captured_image.position.y,
                    "z": captured_image.position.z
                },
                "sequence_index": captured_image.position.sequence_index
            }
        )
    except Exception as e:
        logger.error(f"Failed to capture image at position ({position.x}, {position.y}): {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to capture image: {str(e)}"
        )


@router.post("/session/{session_uid}/stitch", response_model=StitchingResultModel)
@handle_route_errors("stitch", "captured images")
async def stitch_captured_images(
    session_uid: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    stitching_service: ImageStitchingService = Depends(get_service_by_type(ImageStitchingService))
):
    """Process captured images and create stitched panorama."""
    validate_authentication(user, "stitch captured images")
    
    try:
        # Start stitching process
        result = stitching_service.start_stitching_process(session_uid)
        logger.info(f"Stitching process completed for session {session_uid}")
        return result
    except Exception as e:
        logger.error(f"Failed to stitch images for session {session_uid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to stitch images: {str(e)}"
        )


@router.get("/session/{session_uid}/result")
@handle_route_errors("download", "stitching result")
async def download_stitching_result(
    session_uid: str,
    user: dict = Depends(get_current_user),
    stitching_service: ImageStitchingService = Depends(get_service_by_type(ImageStitchingService))
):
    """Download the stitched result image."""
    validate_authentication(user, "download stitching result")
    
    try:
        result_path = stitching_service.get_result_file_path(session_uid)
        
        if not result_path or not os.path.exists(result_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stitching result not found or not yet available"
            )
        
        filename = f"stitched_result_{session_uid}.jpg"
        return FileResponse(
            path=result_path,
            filename=filename,
            media_type="image/jpeg"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve stitching result for session {session_uid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to serve result: {str(e)}"
        )


@router.delete("/session/{session_uid}")
@handle_route_errors("delete", "stitching session")
async def delete_stitching_session(
    session_uid: str,
    user: dict = Depends(get_current_user),
    stitching_service: ImageStitchingService = Depends(get_service_by_type(ImageStitchingService))
):
    """Delete a stitching session and cleanup associated files."""
    validate_authentication(user, "delete stitching session")
    
    try:
        success = stitching_service.delete_session(session_uid)
        if success:
            logger.info(f"Deleted stitching session {session_uid}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"success": True, "message": "Session deleted successfully"}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete stitching session {session_uid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/sessions", response_model=List[StitchingSessionModel])
@handle_route_errors("list", "stitching sessions")
async def list_stitching_sessions(
    user: dict = Depends(get_current_user),
    stitching_service: ImageStitchingService = Depends(get_service_by_type(ImageStitchingService))
):
    """List all active stitching sessions."""
    validate_authentication(user, "list stitching sessions")
    
    try:
        sessions = stitching_service.list_sessions()
        return sessions
    except Exception as e:
        logger.error(f"Failed to list stitching sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for image stitching service."""
    return {
        "status": "healthy",
        "service": "image_stitching",
        "timestamp": "2025-01-25T12:00:00Z"
    }