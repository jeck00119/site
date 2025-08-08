import logging
from typing import Union

logger = logging.getLogger(__name__)

from services.algorithms.algorithms_service import AlgorithmsService
from services.authentication.auth_service import AuthService
from services.camera.camera_service import CameraService
from services.cnc.cnc_service import CncService
from services.components.components_service import ComponentsService
from services.configurations.configurations_service import ConfigurationService
from services.image_source.image_source_service import ImageSourceService
from services.image_source.load_image_service import LoadImageService
from services.inspection_list.inspection_list_service import InspectionListService
from services.logger.logger_service import AppLogger
from services.masks.masks_service import MasksService
from services.media.pygame_audio_service import PygameAudioService
from services.port_manager.port_manager import UnifiedUSBManager
from services.processing.process_service import ProcessService
from services.robot.robot_service import RobotService


class ServiceManager:
    image_source_service: Union[None, ImageSourceService] = None
    camera_service: Union[None, CameraService] = None
    algorithms_service: Union[None, AlgorithmsService] = None
    components_service: Union[None, ComponentsService] = None
    cnc_service: Union[None, CncService] = None
    usb_manager: Union[None, UnifiedUSBManager] = None
    load_image_service: Union[None, LoadImageService] = None
    robot_service: Union[None, RobotService] = None
    process_service: Union[None, ProcessService] = None
    configuration_service: Union[None, ConfigurationService] = None
    audio_service: Union[None, PygameAudioService] = None
    auth_service: Union[None, AuthService] = None
    app_log: Union[None, AppLogger] = None
    masks_service: Union[None, MasksService] = None
    inspection_list_service: Union[None, InspectionListService] = None

    def __init__(self):
        pass

    @classmethod
    def init_services(cls):
        cls.image_source_service = ImageSourceService()
        cls.camera_service = CameraService()
        cls.algorithms_service = AlgorithmsService()
        cls.components_service = ComponentsService()
        cls.cnc_service = CncService()
        cls.usb_manager = UnifiedUSBManager()
        cls.load_image_service = LoadImageService()
        cls.robot_service = RobotService()
        cls.process_service = ProcessService()
        cls.configuration_service = ConfigurationService()
        # Initialize audio service with fallback for systems without audio
        try:
            cls.audio_service = PygameAudioService()
            logger.info("Audio service initialized successfully")
        except Exception as e:
            logger.warning(f"Audio service initialization failed: {e}")
            logger.info("Continuing without audio service - industrial functions will work normally")
            cls.audio_service = None
        cls.auth_service = AuthService()
        cls.app_log = AppLogger()
        cls.app_log.create_handler()
        cls.masks_service = MasksService(cls.image_source_service, cls.load_image_service)
        cls.inspection_list_service = InspectionListService()
        # image_generator = ImageGeneratorService()
        # image_generator.initialize_image_generator()

    @classmethod
    def un_init_services(cls):
        """Gracefully shutdown all services"""
        import asyncio
        from api.ws_connection_manager import ConnectionManager
        
        try:
            # Shutdown CNC service and close serial connections
            if cls.cnc_service:
                try:
                    cls.cnc_service.shutdown_cnc_service()
                except Exception as e:
                    logger.warning(f"Error shutting down CNC service: {e}")
            
            # Close all WebSocket connections - simplified approach
            connection_manager = ConnectionManager()
            if hasattr(connection_manager, 'active_connections'):
                try:
                    # Directly clear connections without async operations during shutdown
                    connection_count = len(connection_manager.active_connections)
                    connection_manager.active_connections.clear()
                    if connection_count > 0:
                        logger.info(f"Cleared {connection_count} WebSocket connections during shutdown")
                except Exception as e:
                    logger.warning(f"Error clearing WebSocket connections during shutdown: {e}")
                    
        except Exception as e:
            logger.warning(f"Error during service cleanup: {e}")
            
        logger.info("Service cleanup completed")
