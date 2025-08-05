from typing import Union

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
from services.port_manager.port_manager import PortManager
from services.processing.process_service import ProcessService
from services.robot.robot_service import RobotService


class ServiceManager:
    image_source_service: Union[None, ImageSourceService] = None
    camera_service: Union[None, CameraService] = None
    algorithms_service: Union[None, AlgorithmsService] = None
    components_service: Union[None, ComponentsService] = None
    cnc_service: Union[None, CncService] = None
    port_manager: Union[None, PortManager] = None
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
        cls.port_manager = PortManager()
        cls.load_image_service = LoadImageService()
        cls.robot_service = RobotService()
        cls.process_service = ProcessService()
        cls.configuration_service = ConfigurationService()
        cls.audio_service = PygameAudioService()
        cls.auth_service = AuthService()
        cls.app_log = AppLogger()
        cls.app_log.create_handler()
        cls.masks_service = MasksService(cls.image_source_service, cls.load_image_service)
        cls.inspection_list_service = InspectionListService()
        # image_generator = ImageGeneratorService()
        # image_generator.initialize_image_generator()

    @classmethod
    def un_init_services(cls):
        pass
