import cv2
import numpy
import logging
import threading
import time
from typing import Optional, Dict
from collections import OrderedDict

from repo.repositories import ImageSourceRepository, CameraCalibrationRepository
from repo.repository_exceptions import UidNotFound
from services.camera.camera_service import CameraService, CameraNotFoundError, CameraFrameError
from services.image_generator.image_generator_service import ImageGeneratorService
from services.image_source.image_source_model import ImageSourceModel, ImgSrcEnum
from src.metaclasses.singleton import Singleton
from src.utils import load_fallback_image

logger = logging.getLogger(__name__)

class ImageSourceError(Exception):
    """Base exception for image source errors"""
    pass

class ImageSourceNotFoundError(ImageSourceError):
    """Raised when image source UID is not found"""
    pass

class ImageValidationError(ImageSourceError):
    """Raised when image validation fails"""
    pass


class ImageSourceService(metaclass=Singleton):
    def __init__(self):
        self._lock = threading.RLock()  # Thread safety
        
        # Image source management
        self.image_sources: dict[str, ImageSourceModel] = {}
        self.live_image_source: ImageSourceModel = None
        
        # Enhanced frame caching with memory management
        self._frame_cache_max_size = 50  # Maximum cached frames
        self._frame_cache_max_age = 300  # 5 minutes in seconds
        self.images_sources_last_frame: OrderedDict[str, Dict] = OrderedDict()
        self._frame_access_times: Dict[str, float] = {}
        
        # Repositories
        self.image_sources_repository = ImageSourceRepository()
        self.camera_calibration_repository = CameraCalibrationRepository()

        # Services
        self.camera_service = CameraService()
        self.image_generator_service = ImageGeneratorService()
        
        # Load fallback image once using centralized function
        self._fallback_image = load_fallback_image()
    
    def _validate_frame(self, frame: numpy.ndarray) -> bool:
        """Validate frame data"""
        if frame is None:
            return False
        if not isinstance(frame, numpy.ndarray):
            return False
        if frame.size == 0:
            return False
        # Check for reasonable dimensions (not too large/small)
        if len(frame.shape) < 2 or len(frame.shape) > 3:
            return False
        height, width = frame.shape[:2]
        if height < 1 or width < 1 or height > 10000 or width > 10000:
            return False
        return True
    
    def _cleanup_frame_cache(self):
        """Clean up old frames from cache to manage memory"""
        current_time = time.time()
        
        # Remove expired frames
        to_remove = []
        for uid, access_time in self._frame_access_times.items():
            if current_time - access_time > self._frame_cache_max_age:
                to_remove.append(uid)
        
        for uid in to_remove:
            self._remove_from_cache(uid)
        
        # Remove oldest frames if cache is too large
        while len(self.images_sources_last_frame) > self._frame_cache_max_size:
            # Remove oldest (first in OrderedDict)
            oldest_uid = next(iter(self.images_sources_last_frame))
            self._remove_from_cache(oldest_uid)
    
    def _remove_from_cache(self, uid: str):
        """Remove frame from cache safely"""
        if uid in self.images_sources_last_frame:
            self.images_sources_last_frame.pop(uid, None)
        if uid in self._frame_access_times:
            self._frame_access_times.pop(uid, None)
        logger.debug(f"Removed frame {uid} from cache")
    
    def _cache_frame(self, uid: str, frame: numpy.ndarray):
        """Cache frame with metadata and cleanup if needed"""
        current_time = time.time()
        
        # Update cache
        self.images_sources_last_frame[uid] = {
            'frame': frame,
            'timestamp': current_time,
            'size': frame.nbytes if frame is not None else 0
        }
        self._frame_access_times[uid] = current_time
        
        # Move to end (most recently used)
        self.images_sources_last_frame.move_to_end(uid)
        
        # Cleanup if needed
        self._cleanup_frame_cache()

    def initialize_all_image_sources(self):
        # Only reinitialize if sources have changed
        import time
        start_time = time.time()
        
        # Get current image sources from repository
        current_sources = self.image_sources_repository.read_all()
        
        # Check if we need to reinitialize
        for img_src in current_sources:
            try:
                uid = img_src['uid']
                # Skip if already initialized with same settings
                if uid in self.image_sources:
                    # Image source already initialized, skip
                    continue
                else:
                    # New or changed image source, initialize it
                    self._initialize_image_source_by_uid(uid)
            except:
                pass
        
        # Remove sources that are no longer in the repository
        current_uids = {src['uid'] for src in current_sources}
        sources_to_remove = [uid for uid in self.image_sources.keys() if uid not in current_uids]
        for uid in sources_to_remove:
            self._uninitialize_image_source_by_uid(uid)
        
        print(f"[IMAGE-SOURCE-SERVICE] Initialization took {time.time() - start_time:.3f}s")

    def grab_from_image_source(self, uid: str, raise_on_error: bool = False) -> numpy.ndarray:
        """
        Grab frame from image source with proper validation and caching
        
        Args:
            uid: Image source unique identifier
            raise_on_error: If True, raise exceptions instead of returning fallback images
            
        Returns:
            numpy.ndarray: Image frame
            
        Raises:
            ImageSourceNotFoundError: If image source not found (when raise_on_error=True)
            ImageValidationError: If frame validation fails (when raise_on_error=True)
        """
        with self._lock:
            try:
                # Default to fallback image
                image = self._fallback_image
                
                if uid not in self.image_sources:
                    error_msg = f"Image source {uid} not found or not initialized"
                    # Only log once per uid to avoid spam
                    if uid not in getattr(self, '_logged_missing_sources', set()):
                        logger.warning(error_msg)
                        if not hasattr(self, '_logged_missing_sources'):
                            self._logged_missing_sources = set()
                        self._logged_missing_sources.add(uid)
                    if raise_on_error:
                        raise ImageSourceNotFoundError(error_msg)
                    self._cache_frame(uid, image)
                    return image

                image_source = self.image_sources[uid]
                
                try:
                    # Grab from appropriate source
                    if image_source.image_source_type == ImgSrcEnum.DYNAMIC:
                        if not image_source.camera_uid:
                            error_msg = f"Image source {uid} has no camera UID configured"
                            logger.error(error_msg)
                            if raise_on_error:
                                raise ImageValidationError(error_msg)
                        else:
                            image = self.camera_service.grab_from_camera(
                                image_source.camera_uid, 
                                raise_on_error=raise_on_error
                            )
                    
                    elif image_source.image_source_type == ImgSrcEnum.STATIC:
                        if not image_source.image_generator_uid:
                            error_msg = f"Image source {uid} has no generator UID configured"
                            logger.error(error_msg)
                            if raise_on_error:
                                raise ImageValidationError(error_msg)
                        else:
                            image = self.image_generator_service.grab_from_generator(
                                image_source.image_generator_uid
                            )
                    
                    else:
                        error_msg = f"Unknown image source type for {uid}: {image_source.image_source_type}"
                        logger.error(error_msg)
                        if raise_on_error:
                            raise ImageValidationError(error_msg)

                except (CameraNotFoundError, CameraFrameError) as e:
                    logger.error(f"Camera error for image source {uid}: {str(e)}")
                    if raise_on_error:
                        raise ImageValidationError(f"Camera error: {str(e)}")
                    image = self._fallback_image

                # Validate the frame
                if not self._validate_frame(image):
                    error_msg = f"Invalid frame from image source {uid}"
                    logger.warning(error_msg)
                    if raise_on_error:
                        raise ImageValidationError(error_msg)
                    image = self._fallback_image

                # Cache the frame
                self._cache_frame(uid, image)
                return image

            except (ImageSourceNotFoundError, ImageValidationError):
                raise  # Re-raise our custom exceptions
            except Exception as e:
                error_msg = f"Unexpected error grabbing from image source {uid}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                if raise_on_error:
                    raise ImageValidationError(error_msg)
                self._cache_frame(uid, self._fallback_image)
                return self._fallback_image

    def get_frame(self, uid: str) -> numpy.ndarray:
        """Get cached frame with validation and access time update"""
        with self._lock:
            if uid not in self.images_sources_last_frame:
                logger.warning(f"Requested frame for {uid} not in cache, grabbing fresh frame")
                return self.grab_from_image_source(uid)
            
            # Update access time for LRU cache
            current_time = time.time()
            self._frame_access_times[uid] = current_time
            
            # Move to end (most recently accessed)
            self.images_sources_last_frame.move_to_end(uid)
            
            frame_data = self.images_sources_last_frame[uid]
            
            # Handle both old and new cache formats
            if isinstance(frame_data, dict):
                return frame_data['frame']
            else:
                # Legacy format - migrate to new format
                self._cache_frame(uid, frame_data)
                return frame_data

    def on_patch_image_source(self, image_source: ImageSourceModel):
        self._uninitialize_image_source_by_uid(image_source.uid)
        self._initialize_image_source_by_uid(image_source.uid)

    def on_delete_image_source(self, image_source_id):
        self._uninitialize_image_source_by_uid(image_source_id)

    def _initialize_image_source_by_uid(self, uid):
        if uid not in self.image_sources.keys():
            image_source_model = ImageSourceModel(**self.image_sources_repository.read_id(uid))

            if image_source_model.image_source_type == ImgSrcEnum.DYNAMIC:
                if image_source_model.camera_uid != '':
                    self.camera_service.initialize_camera(image_source_model.camera_uid)
                    self.camera_service.load_setting_file(image_source_model.camera_uid,
                                                          image_source_model.camera_settings_uid)
                self.image_sources[uid] = image_source_model
                
                # Clear the logged missing source flag when initialized
                if hasattr(self, '_logged_missing_sources') and uid in self._logged_missing_sources:
                    self._logged_missing_sources.discard(uid)

            elif image_source_model.image_source_type == ImgSrcEnum.STATIC:
                if image_source_model.image_generator_uid != '':
                    self.image_generator_service.initialize_generator(image_source_model.image_generator_uid)
                self.image_sources[uid] = image_source_model
                
                # Clear the logged missing source flag when initialized
                if hasattr(self, '_logged_missing_sources') and uid in self._logged_missing_sources:
                    self._logged_missing_sources.discard(uid)
        else:
            return ' '

    def _uninitialize_image_source_by_uid(self, uid):
        if uid not in self.image_sources.keys():
           return
        else:
            if self.image_sources[uid].image_source_type == ImgSrcEnum.DYNAMIC:
               # self.camera_service.release_camera(self.image_sources[uid].camera_uid)
               self.image_sources.pop(uid)
            elif self.image_sources[uid].image_source_type == ImgSrcEnum.STATIC:
                self.image_sources.pop(uid)

    def load_settings_to_image_source(self, uid):
        # Ensure image source is initialized in cache
        if uid not in self.image_sources:
            try:
                self._initialize_image_source_by_uid(uid)
            except Exception as e:
                logger.error(f"Failed to initialize image source {uid}: {e}")
                return
        
        # Proceed only if image source is now in cache
        if uid in self.image_sources:
            settings_uid = self.image_sources[uid].camera_settings_uid
            camera_uid = self.image_sources[uid].camera_uid
            
            self.camera_service.load_setting_file(camera_uid, settings_uid)

    def check_image_source_type(self, uid):
        image_source_model = ImageSourceModel(**self.image_sources_repository.read_id(uid))

        if image_source_model.image_source_type == ImgSrcEnum.DYNAMIC:
            return image_source_model.image_source_type

        elif image_source_model.image_source_type == ImgSrcEnum.STATIC:
            return image_source_model.image_source_type

    def get_calibration_uid(self, uid):
        if uid in self.image_sources.keys():
            return self.image_sources.get(uid).camera_calibration_uid
        return None
