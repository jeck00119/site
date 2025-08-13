import cv2
import logging
import threading
from typing import Optional

from repo.repositories import CameraSettingsRepository, CameraRepository
from repo.repository_exceptions import UidNotFound
from services.camera.camera_factory import CameraFactory
from services.camera.camera_model import CameraModel, EnumCameraTypes, WebCamSettingsModel, BaslerSettingsModel
from services.camera.implementation.basler_camera import BaslerCamera
from services.camera.implementation.interface_camera import CameraInterface
from src.metaclasses.singleton import Singleton
from src.utils import load_fallback_image

logger = logging.getLogger(__name__)

class CameraError(Exception):
    """Base exception for camera-related errors"""
    pass

class CameraNotFoundError(CameraError):
    """Raised when camera UID is not found"""
    pass

class CameraInitializationError(CameraError):
    """Raised when camera fails to initialize"""
    pass

class CameraFrameError(CameraError):
    """Raised when frame capture fails"""
    pass


class CameraService(metaclass=Singleton):
    def __init__(self):
        self._is_initialized = False
        self._lock = threading.RLock()  # Reentrant lock for thread safety

        self.cameras: dict[str, CameraInterface] = {}
        self.camera_repository = CameraRepository()
        self.camera_settings_repository = CameraSettingsRepository()
        
        # Load fallback images once at initialization using centralized function
        self._fallback_images = {
            'no_camera': load_fallback_image('assets/no_camera.jpg'),
            'cap_not_opened': load_fallback_image('assets/cap_not_opened.png')
        }

    def initialize_all_cameras(self):
        import time
        print(f"[CAMERA-SERVICE] Starting to initialize all cameras at {time.time()}")
        for cam_doc in self.camera_repository.read_all():
            self.initialize_camera(cam_doc['uid'])
        print(f"[CAMERA-SERVICE] Finished initializing all cameras at {time.time()}")

    def find_basler_cameras(self):
        return BaslerCamera.find_cameras()

    def initialize_camera(self, uid: str) -> str:
        """Initialize camera with proper error handling and thread safety"""
        with self._lock:
            try:
                if uid in self.cameras:
                    logger.info(f"Camera {uid} already initialized")
                    return f"Camera {uid} already initialized"
                
                # Get camera configuration from database
                try:
                    cam_doc = self.camera_repository.read_id(uid)
                except UidNotFound:
                    error_msg = f"Camera with id {uid} not found in database"
                    logger.error(error_msg)
                    raise CameraNotFoundError(error_msg)
                
                if not cam_doc:
                    error_msg = f"Camera configuration for {uid} is empty"
                    logger.error(error_msg)
                    raise CameraNotFoundError(error_msg)
                
                # Create and initialize camera
                try:
                    camera_model = CameraModel(**cam_doc)
                    camera = CameraFactory.create_camera(camera_model)
                    
                    # Initialize with timeout or retries if needed
                    result = camera.initialize()
                    
                    # Verify initialization was successful
                    if not result or not hasattr(camera, 'initialized') or not camera.initialized:
                        error_msg = f"Camera {uid} initialization failed: {result}"
                        logger.error(error_msg)
                        # Clean up failed camera
                        try:
                            camera.release()
                        except Exception:
                            pass
                        raise CameraInitializationError(error_msg)
                    
                    # Store successfully initialized camera
                    self.cameras[uid] = camera
                    success_msg = f"Camera {uid} initialized successfully"
                    logger.info(success_msg)
                    return success_msg
                    
                except Exception as e:
                    error_msg = f"Failed to initialize camera {uid}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    raise CameraInitializationError(error_msg)
                    
            except (CameraNotFoundError, CameraInitializationError):
                raise  # Re-raise our custom exceptions
            except Exception as e:
                error_msg = f"Unexpected error initializing camera {uid}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise CameraInitializationError(error_msg)

    def release_camera(self, uid: str) -> str:
        """Release camera with proper error handling and cleanup"""
        with self._lock:
            try:
                if uid not in self.cameras:
                    logger.warning(f"Attempted to release non-initialized camera: {uid}")
                    return f"Camera with id {uid} is not initialized"
                
                camera = self.cameras[uid]
                
                # Release camera resources
                try:
                    camera.release()
                    logger.info(f"Camera {uid} resources released successfully")
                except Exception as e:
                    logger.error(f"Error releasing camera {uid} resources: {e}")
                    # Continue with removal even if release fails
                
                # Remove from active cameras
                self.cameras.pop(uid)
                success_msg = f"Camera with id {uid} has been released"
                logger.info(success_msg)
                return success_msg
                
            except Exception as e:
                error_msg = f"Error releasing camera {uid}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                # Force remove from dictionary even if release failed
                if uid in self.cameras:
                    self.cameras.pop(uid)
                return error_msg

    def patch_camera(self, camera_model: CameraModel):
        self.release_camera(camera_model.uid)
        self.initialize_camera(camera_model.uid)

    def post_camera(self, camera_model: CameraModel):
        self.initialize_camera(camera_model.uid)

    def delete_camera(self, camera_uid):
        self.release_camera(camera_uid)

    def load_setting_file(self, uid, camera_setting_uid):
        if uid in self.cameras.keys():
            try:
                camera_settings = self.camera_settings_repository.read_id(camera_setting_uid)
                if self.cameras[uid].type == EnumCameraTypes.basler_usb:
                    camera_settings = BaslerSettingsModel(**camera_settings)
                else:
                    camera_settings = WebCamSettingsModel(**camera_settings)

                if camera_settings:
                    self.cameras[uid].load_config(camera_settings.model_dump())
                return f'Camera settings {camera_setting_uid} loaded.'
            except UidNotFound:
                pass
        else:
            return f'Camera with id {uid} dosent exist/is not initialized.'

    def load_settings_from_dict(self, camera_uid, settings):
        self.cameras[camera_uid].load_config(settings)

    def change_camera_prop(self, uid, name, value):
        if uid in self.cameras.keys():
            self.cameras[uid].set(name, value)
        else:
            return f'Camera with id {uid} dosent exist/is not initialized.'

    def grab_from_camera(self, uid: str, raise_on_error: bool = False):
        """
        Grab frame from camera with proper error handling
        
        Args:
            uid: Camera unique identifier
            raise_on_error: If True, raise exceptions instead of returning fallback images
            
        Returns:
            numpy.ndarray: Camera frame or fallback image
            
        Raises:
            CameraNotFoundError: If camera not found (when raise_on_error=True)
            CameraFrameError: If frame capture fails (when raise_on_error=True)
        """
        try:
            # Check if camera exists
            if uid not in self.cameras:
                error_msg = f"Camera {uid} is not initialized"
                logger.error(error_msg)
                if raise_on_error:
                    raise CameraNotFoundError(error_msg)
                fallback = self._fallback_images.get('no_camera')
                return fallback if fallback is not None else load_fallback_image()

            camera = self.cameras[uid]
            
            # Handle different camera types
            if camera.type == EnumCameraTypes.basler_usb:
                try:
                    frame = camera.get_frame()
                    if frame is None:
                        error_msg = f"Basler camera {uid} returned None frame"
                        logger.warning(error_msg)
                        if raise_on_error:
                            raise CameraFrameError(error_msg)
                        fallback = self._fallback_images.get('no_camera')
                        return fallback if fallback is not None else load_fallback_image()
                    return frame
                except Exception as e:
                    error_msg = f"Error capturing from Basler camera {uid}: {str(e)}"
                    logger.error(error_msg)
                    if raise_on_error:
                        raise CameraFrameError(error_msg)
                    fallback = self._fallback_images.get('no_camera')
                    return fallback if fallback is not None else load_fallback_image()

            elif camera.type in [EnumCameraTypes.webcam_logi, EnumCameraTypes.webcam_msft]:
                try:
                    # Check if webcam is opened
                    if not hasattr(camera, '_cap') or not camera._cap.isOpened():
                        error_msg = f"WebCam {uid} is not opened"
                        logger.warning(error_msg)
                        if raise_on_error:
                            raise CameraFrameError(error_msg)
                        fallback = self._fallback_images.get('cap_not_opened')
                        return fallback if fallback is not None else load_fallback_image('assets/cap_not_opened.png')
                    
                    frame = camera.get_frame()
                    if frame is None:
                        error_msg = f"WebCam {uid} returned None frame"
                        logger.warning(error_msg)
                        if raise_on_error:
                            raise CameraFrameError(error_msg)
                        fallback = self._fallback_images.get('cap_not_opened')
                        return fallback if fallback is not None else load_fallback_image('assets/cap_not_opened.png')
                    return frame
                except Exception as e:
                    error_msg = f"Error capturing from WebCam {uid}: {str(e)}"
                    logger.error(error_msg)
                    if raise_on_error:
                        raise CameraFrameError(error_msg)
                    fallback = self._fallback_images.get('cap_not_opened')
                    return fallback if fallback is not None else load_fallback_image('assets/cap_not_opened.png')
            else:
                error_msg = f"Unknown camera type for {uid}: {camera.type}"
                logger.error(error_msg)
                if raise_on_error:
                    raise CameraFrameError(error_msg)
                fallback = self._fallback_images.get('no_camera')
                return fallback if fallback is not None else load_fallback_image()
                
        except (CameraNotFoundError, CameraFrameError):
            raise  # Re-raise our custom exceptions
        except Exception as e:
            error_msg = f"Unexpected error grabbing frame from camera {uid}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if raise_on_error:
                raise CameraFrameError(error_msg)
            fallback = self._fallback_images.get('no_camera')
            return fallback if fallback is not None else load_fallback_image()
