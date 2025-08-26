import cv2
import numpy as np
import os
import time
import logging
import threading
import uuid
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from services.camera.camera_service import CameraService
from services.image_source.image_source_service import ImageSourceService
from services.image_stitching.image_stitching_models import (
    ImageStitchingConfigModel, 
    StitchingSessionModel,
    StitchingStatus,
    CapturePositionModel,
    CapturedImageModel,
    StitchingProgressModel,
    StitchingResultModel,
    StitchingPattern
)
from src.metaclasses.singleton import Singleton
# from src.utils import formatPrecision  # Not available in backend utils

logger = logging.getLogger(__name__)


class ImageStitchingError(Exception):
    """Base exception for image stitching errors"""
    pass


class StitchingConfigurationError(ImageStitchingError):
    """Raised when stitching configuration is invalid"""
    pass


class StitchingCaptureError(ImageStitchingError):
    """Raised when image capture fails"""
    pass


class StitchingProcessError(ImageStitchingError):
    """Raised when stitching process fails"""
    pass


class ImageStitchingService(metaclass=Singleton):
    """
    Service for managing image stitching operations.
    Handles grid-based image capture and OpenCV-based panorama stitching.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        self._sessions: Dict[str, StitchingSessionModel] = {}
        
        # Service dependencies
        self.camera_service = CameraService()
        self.image_source_service = ImageSourceService()
        
        # Storage paths
        self.base_data_path = Path("data/image_stitching")
        self.base_reports_path = Path("reports/stitching_results")
        
        # Create storage directories
        self._ensure_directories()
        
        logger.info("ImageStitchingService initialized")

    def _ensure_directories(self):
        """Create necessary storage directories"""
        try:
            self.base_data_path.mkdir(parents=True, exist_ok=True)
            self.base_reports_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directories: {self.base_data_path}, {self.base_reports_path}")
        except Exception as e:
            logger.error(f"Failed to create storage directories: {e}")
            raise ImageStitchingError(f"Failed to create storage directories: {e}")

    def create_stitching_session(self, config: ImageStitchingConfigModel) -> StitchingSessionModel:
        """
        Create a new stitching session with the given configuration.
        
        Args:
            config: Stitching configuration
            
        Returns:
            Created session model
            
        Raises:
            StitchingConfigurationError: If configuration is invalid
        """
        try:
            with self._lock:
                # Validate configuration
                self._validate_configuration(config)
                
                # Generate grid positions
                positions = self._generate_grid_positions(config)
                
                # Create session
                session = StitchingSessionModel(
                    uid=config.uid,
                    config=config,
                    status=StitchingStatus.IDLE,
                    total_positions=len(positions),
                    created_at=time.time()
                )
                
                # Create session directory
                session_dir = self.base_data_path / config.uid
                session_dir.mkdir(exist_ok=True)
                
                self._sessions[config.uid] = session
                
                logger.info(f"Created stitching session {config.uid} with {len(positions)} positions")
                return session
                
        except Exception as e:
            logger.error(f"Failed to create stitching session: {e}")
            raise StitchingConfigurationError(f"Failed to create stitching session: {e}")

    def _validate_configuration(self, config: ImageStitchingConfigModel):
        """Validate stitching configuration"""
        # Check if camera exists and is initialized
        if config.camera_uid not in self.camera_service.cameras:
            raise StitchingConfigurationError(f"Camera {config.camera_uid} is not initialized")
        
        # Validate working area dimensions
        if config.working_area_x <= 0 or config.working_area_y <= 0:
            raise StitchingConfigurationError("Working area dimensions must be positive")
        
        # Validate step sizes
        if config.step_size_x <= 0 or config.step_size_y <= 0:
            raise StitchingConfigurationError("Step sizes must be positive")
        
        # Calculate grid size and warn if too large
        grid_points = self._calculate_grid_size(config)
        if grid_points > 1000:
            raise StitchingConfigurationError(f"Grid too dense ({grid_points} points). Reduce step size or working area.")

    def _calculate_grid_size(self, config: ImageStitchingConfigModel) -> int:
        """Calculate total number of grid points"""
        steps_x = int(np.ceil(config.working_area_x / config.step_size_x)) + 1
        steps_y = int(np.ceil(config.working_area_y / config.step_size_y)) + 1
        return steps_x * steps_y

    def _generate_grid_positions(self, config: ImageStitchingConfigModel) -> List[CapturePositionModel]:
        """
        Generate grid positions based on configuration.
        
        Args:
            config: Stitching configuration
            
        Returns:
            List of capture positions
        """
        positions = []
        
        steps_x = int(np.ceil(config.working_area_x / config.step_size_x))
        steps_y = int(np.ceil(config.working_area_y / config.step_size_y))
        
        sequence_index = 0
        
        for row in range(steps_y + 1):
            y = min(row * config.step_size_y, config.working_area_y)
            
            for col in range(steps_x + 1):
                x = col * config.step_size_x
                
                # Apply zigzag pattern if selected
                if config.pattern == StitchingPattern.ZIGZAG and row % 2 == 1:
                    x = config.working_area_x - x  # Reverse direction on odd rows
                
                x = min(x, config.working_area_x)
                
                position = CapturePositionModel(
                    x=round(x, 2),
                    y=round(y, 2),
                    z=round(config.z_height, 2),
                    sequence_index=sequence_index
                )
                positions.append(position)
                sequence_index += 1
        
        logger.debug(f"Generated {len(positions)} grid positions for pattern {config.pattern}")
        return positions

    def capture_image_at_position(self, session_uid: str, position: CapturePositionModel) -> CapturedImageModel:
        """
        Capture image at specified position.
        
        Args:
            session_uid: Session identifier
            position: Capture position
            
        Returns:
            Captured image metadata
            
        Raises:
            StitchingCaptureError: If capture fails
        """
        try:
            with self._lock:
                session = self._get_session(session_uid)
                
                # Grab frame from camera
                frame = self.camera_service.grab_from_camera(
                    session.config.camera_uid, 
                    raise_on_error=True
                )
                
                # Generate unique filename
                image_uid = str(uuid.uuid4())
                filename = f"capture_{position.sequence_index:04d}_{position.x:.1f}_{position.y:.1f}.jpg"
                file_path = self.base_data_path / session_uid / filename
                
                # Save image to disk
                success = cv2.imwrite(str(file_path), frame)
                if not success:
                    raise StitchingCaptureError(f"Failed to save image to {file_path}")
                
                # Create captured image metadata
                captured_image = CapturedImageModel(
                    uid=image_uid,
                    position=position,
                    timestamp=time.time(),
                    file_path=str(file_path),
                    camera_uid=session.config.camera_uid
                )
                
                # Update session
                session.captured_images.append(captured_image)
                session.completed_positions += 1
                
                logger.debug(f"Captured image {len(session.captured_images)}/{session.total_positions} at position ({position.x}, {position.y})")
                
                return captured_image
                
        except Exception as e:
            logger.error(f"Failed to capture image at position ({position.x}, {position.y}): {e}")
            raise StitchingCaptureError(f"Failed to capture image: {e}")

    def start_stitching_process(self, session_uid: str) -> StitchingResultModel:
        """
        Process captured images and create stitched panorama.
        
        Args:
            session_uid: Session identifier
            
        Returns:
            Stitching result
            
        Raises:
            StitchingProcessError: If stitching fails
        """
        try:
            with self._lock:
                session = self._get_session(session_uid)
                
                if len(session.captured_images) < 2:
                    raise StitchingProcessError("Need at least 2 images for stitching")
                
                session.status = StitchingStatus.PROCESSING
                start_time = time.time()
                
                # Load images
                logger.info(f"Loading {len(session.captured_images)} images for stitching")
                images = []
                for captured_image in session.captured_images:
                    img = cv2.imread(captured_image.file_path)
                    if img is None:
                        raise StitchingProcessError(f"Failed to load image: {captured_image.file_path}")
                    images.append(img)
                
                # Perform stitching using OpenCV
                logger.info("Starting OpenCV stitching process")
                stitched_image = self._stitch_images(images)
                
                # Save result
                result_filename = f"stitched_result_{session_uid}_{int(time.time())}.jpg"
                result_path = self.base_reports_path / result_filename
                
                success = cv2.imwrite(str(result_path), stitched_image)
                if not success:
                    raise StitchingProcessError(f"Failed to save stitched image to {result_path}")
                
                # Update session
                processing_time = time.time() - start_time
                session.status = StitchingStatus.COMPLETED
                session.result_image_path = str(result_path)
                session.completed_at = time.time()
                
                # Create result model
                result = StitchingResultModel(
                    session_uid=session_uid,
                    success=True,
                    result_image_path=str(result_path),
                    result_image_url=f"/api/image_stitching/result/{session_uid}",
                    captured_image_count=len(session.captured_images),
                    processing_time_seconds=processing_time,
                    image_dimensions=(stitched_image.shape[1], stitched_image.shape[0])
                )
                
                logger.info(f"Stitching completed in {processing_time:.2f}s. Result: {result_path}")
                return result
                
        except Exception as e:
            # Update session with error
            if session_uid in self._sessions:
                session = self._sessions[session_uid]
                session.status = StitchingStatus.FAILED
                session.error_message = str(e)
            
            logger.error(f"Stitching process failed: {e}")
            raise StitchingProcessError(f"Stitching failed: {e}")

    def _stitch_images(self, images: List[np.ndarray]) -> np.ndarray:
        """
        Stitch images using OpenCV Stitcher.
        
        Args:
            images: List of images to stitch
            
        Returns:
            Stitched panorama image
            
        Raises:
            StitchingProcessError: If stitching fails
        """
        try:
            # Create stitcher instance
            stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)
            
            # Configure stitcher for better results with grid patterns
            stitcher.setPanoConfidenceThresh(0.3)  # Lower confidence threshold for grid patterns
            
            # Perform stitching
            logger.debug(f"Stitching {len(images)} images using OpenCV")
            status, stitched = stitcher.stitch(images)
            
            if status != cv2.Stitcher_OK:
                error_messages = {
                    cv2.Stitcher_ERR_NEED_MORE_IMGS: "Need more images",
                    cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL: "Homography estimation failed", 
                    cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL: "Camera parameters adjustment failed"
                }
                error_msg = error_messages.get(status, f"Unknown stitching error (status: {status})")
                raise StitchingProcessError(error_msg)
            
            logger.debug(f"Stitching successful. Result dimensions: {stitched.shape}")
            return stitched
            
        except cv2.error as e:
            logger.error(f"OpenCV stitching error: {e}")
            raise StitchingProcessError(f"OpenCV stitching error: {e}")

    def get_session_progress(self, session_uid: str) -> StitchingProgressModel:
        """
        Get progress information for a stitching session.
        
        Args:
            session_uid: Session identifier
            
        Returns:
            Progress information
        """
        try:
            with self._lock:
                session = self._get_session(session_uid)
                
                progress_percent = 0.0
                if session.total_positions > 0:
                    if session.status == StitchingStatus.CAPTURING:
                        # During capture: 0-90% based on completed positions
                        progress_percent = (session.completed_positions / session.total_positions) * 90.0
                    elif session.status == StitchingStatus.PROCESSING:
                        progress_percent = 90.0  # Fixed at 90% during processing
                    elif session.status == StitchingStatus.COMPLETED:
                        progress_percent = 100.0
                
                # Get current position if capturing
                current_position = None
                if session.status == StitchingStatus.CAPTURING and session.completed_positions < session.total_positions:
                    positions = self._generate_grid_positions(session.config)
                    if session.completed_positions < len(positions):
                        current_position = positions[session.completed_positions]
                
                return StitchingProgressModel(
                    session_uid=session_uid,
                    status=session.status,
                    progress_percent=progress_percent,
                    current_position=current_position,
                    completed_positions=session.completed_positions,
                    total_positions=session.total_positions,
                    message=self._get_status_message(session),
                    error_message=session.error_message
                )
                
        except Exception as e:
            logger.error(f"Failed to get session progress: {e}")
            raise ImageStitchingError(f"Failed to get session progress: {e}")

    def _get_status_message(self, session: StitchingSessionModel) -> str:
        """Generate status message for session"""
        if session.status == StitchingStatus.IDLE:
            return "Session created, ready to start"
        elif session.status == StitchingStatus.CAPTURING:
            return f"Capturing images: {session.completed_positions}/{session.total_positions}"
        elif session.status == StitchingStatus.PROCESSING:
            return "Processing captured images..."
        elif session.status == StitchingStatus.COMPLETED:
            return f"Stitching completed successfully! Processed {len(session.captured_images)} images"
        elif session.status == StitchingStatus.FAILED:
            return f"Stitching failed: {session.error_message}"
        else:
            return "Unknown status"

    def get_session(self, session_uid: str) -> StitchingSessionModel:
        """Get session by UID"""
        return self._get_session(session_uid)

    def _get_session(self, session_uid: str) -> StitchingSessionModel:
        """Internal method to get session with validation"""
        if session_uid not in self._sessions:
            raise ImageStitchingError(f"Session {session_uid} not found")
        return self._sessions[session_uid]

    def delete_session(self, session_uid: str) -> bool:
        """
        Delete a stitching session and cleanup files.
        
        Args:
            session_uid: Session identifier
            
        Returns:
            True if session was deleted successfully
        """
        try:
            with self._lock:
                if session_uid not in self._sessions:
                    return False
                
                session = self._sessions[session_uid]
                
                # Cleanup session directory
                session_dir = self.base_data_path / session_uid
                if session_dir.exists():
                    import shutil
                    shutil.rmtree(session_dir, ignore_errors=True)
                
                # Remove from sessions
                del self._sessions[session_uid]
                
                logger.info(f"Deleted stitching session {session_uid}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete session {session_uid}: {e}")
            return False

    def list_sessions(self) -> List[StitchingSessionModel]:
        """List all active stitching sessions"""
        with self._lock:
            return list(self._sessions.values())

    def get_result_file_path(self, session_uid: str) -> Optional[str]:
        """Get file path for stitching result"""
        try:
            session = self._get_session(session_uid)
            return session.result_image_path
        except:
            return None