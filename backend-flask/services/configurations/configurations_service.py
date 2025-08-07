import os
import pathlib
import shutil

from repo.repositories import ConfigurationRepository, AlgorithmsRepository, CameraRepository, CameraSettingsRepository, \
    CncRepository, ComponentsRepository, CustomComponentsRepository, ImageGeneratorRepository, ImageSourceRepository, \
    InspectionsRepository, LocationRepository, ProfilometerRepository, ReferencesRepository, \
    RobotRepository, IdentificationsRepository, AudioEventsRepository, CameraCalibrationRepository, \
    StereoCalibrationRepository, RobotPositionsRepository
from services.camera.camera_service import CameraService
from services.cnc.cnc_service import CncService
from services.components.components_service import ComponentsService
from services.configurations.configuration_model import ConfigurationModel
from services.image_source.image_source_service import ImageSourceService
from services.robot.robot_service import RobotService
from src.metaclasses.singleton import Singleton

directory_path = str(pathlib.Path(__file__).parent.parent.parent.resolve())


class ConfigurationService(metaclass=Singleton):
    def __init__(self):
        self.configuration_repository = ConfigurationRepository()
        self.algorithms_repository = AlgorithmsRepository()
        self.camera_repository = CameraRepository()
        self.camera_settings_repository = CameraSettingsRepository()
        self.cnc_repository = CncRepository()
        self.components_repository = ComponentsRepository()
        self.identifications_repository = IdentificationsRepository()
        self.custom_components_repository = CustomComponentsRepository()
        self.image_generator_repository = ImageGeneratorRepository()
        self.image_source_repository = ImageSourceRepository()
        self.inspections_repository = InspectionsRepository()
        self.locations_repository = LocationRepository()
        self.profilometer_repository = ProfilometerRepository()
        self.references_repository = ReferencesRepository()
        self.robot_repository = RobotRepository()
        self.audio_repository = AudioEventsRepository()
        self.camera_calibration_repository = CameraCalibrationRepository()
        self.stereo_calibration_repository = StereoCalibrationRepository()
        self.robot_positions_repository = RobotPositionsRepository()

        self.image_source_service = ImageSourceService()
        self.camera_service = CameraService()
        self.components_service = ComponentsService()
        self.cnc_service = CncService()
        self.robot_service = RobotService()

        self.current_configuration_uid = None

        self.configuration_changed_socket = False
        self.configuration_changed_process = False

    def get_current_configuration_uid(self):
        return self.current_configuration_uid

    @staticmethod
    def post_configuration(configuration_model: ConfigurationModel):
        config_name = configuration_model.name
        path = directory_path + "/config_db/" + config_name
        os.mkdir(path)

    def copy_configuration(self, configuration_model: ConfigurationModel, original_configuration_uid: str):
        self.post_configuration(configuration_model)
        original_config = self.configuration_repository.read_id(original_configuration_uid)

        shutil.copytree(directory_path + "/config_db/" + original_config['name'],
                        directory_path + "/config_db/" + configuration_model.name, dirs_exist_ok=True)

    @staticmethod
    def delete_configuration(configuration_model: ConfigurationModel):
        name = configuration_model.name
        path = directory_path + "/config_db/" + name
        shutil.rmtree(path)

    @staticmethod
    def update_configuration(old_configuration: ConfigurationModel, configuration_model: ConfigurationModel):
        old_name = old_configuration.name
        old_path = directory_path + "/config_db/" + old_name
        new_name = configuration_model.name
        new_path = directory_path + "/config_db/" + new_name
        os.rename(old_path, new_path)

    def load_configuration(self, configuration_uid):
        configuration = self.configuration_repository.read_id(configuration_uid)
        configuration_model = ConfigurationModel(**configuration)

        # reset all repositories
        self.set_repositories(configuration_model.name)

        self.reinit_services()
        self.set_configuration_flag()

        self.current_configuration_uid = configuration_uid

    def load_configuration_part_number(self, part_number):
        try:
            configuration = self.configuration_repository.read_part_number(part_number)
            configuration_model = ConfigurationModel(**configuration)
            print(f"Configuration Model: {configuration_model}")

            if self.current_configuration_uid != configuration_model.uid:
                print(f"Changing configuration")
                self.set_repositories(configuration_model.name)

                self.reinit_services()

                self.current_configuration_uid = configuration_model.uid
                self.set_configuration_flag()

            return configuration_model
        except Exception as e:
            print(f"Exception when loading config: {e}")
            return None

    def reset_configuration_flag_socket(self):
        self.configuration_changed_socket = False

    def reset_configuration_flag_process(self):
        self.configuration_changed_process = False

    def set_configuration_flag(self):
        self.configuration_changed_socket = True
        self.configuration_changed_process = True

    def get_configuration_flag_socket(self):
        return self.configuration_changed_socket

    def get_configuration_flag_process(self):
        return self.configuration_changed_process

    def set_repositories(self, name):
        self.algorithms_repository.set_db(name)
        self.camera_repository.set_db(name)
        self.camera_settings_repository.set_db(name)
        self.cnc_repository.set_db(name)
        self.components_repository.set_db(name)
        self.identifications_repository.set_db(name)
        self.custom_components_repository.set_db(name)
        self.image_generator_repository.set_db(name)
        self.image_source_repository.set_db(name)
        self.inspections_repository.set_db(name)
        self.locations_repository.set_db(name)
        self.profilometer_repository.set_db(name)
        self.references_repository.set_db(name)
        self.robot_repository.set_db(name)
        self.audio_repository.set_db(name)
        self.camera_calibration_repository.set_db(name)
        self.stereo_calibration_repository.set_db(name)
        self.robot_positions_repository.set_db(name)
        
        # FIXED: Users should remain global, not configuration-specific
        # Removing user repository switching to prevent authentication issues
        # Users database should always point to the main config_db directory
        # from api.dependencies.services import get_service_by_type
        # from services.authentication.auth_service import AuthService
        # auth_service = get_service_by_type(AuthService)()
        # auth_service.users_repository.set_db(name)  # REMOVED - causes users to disappear
        print(f"[DEBUG] Configuration switched to: {name} (users remain global)")

    def reset_dbs(self):
        self.algorithms_repository.reset_db()
        self.camera_repository.reset_db()
        self.camera_settings_repository.reset_db()
        self.cnc_repository.reset_db()
        self.components_repository.reset_db()
        self.identifications_repository.reset_db()
        self.custom_components_repository.reset_db()
        self.image_generator_repository.reset_db()
        self.image_source_repository.reset_db()
        self.inspections_repository.reset_db()
        self.locations_repository.reset_db()
        self.profilometer_repository.reset_db()
        self.references_repository.reset_db()
        self.robot_repository.reset_db()
        self.audio_repository.reset_db()
        self.camera_calibration_repository.reset_db()
        self.stereo_calibration_repository.reset_db()
        self.robot_positions_repository.reset_db()

        self.current_configuration_uid = None

    def reinit_services(self):
        self.image_source_service.initialize_all_image_sources()
        self.camera_service.initialize_all_cameras()
        self.components_service.start_service()
        self.cnc_service.start_cnc_service()
        self.robot_service.start_robot_service()

    def get_current_configuration_name(self):
        if self.current_configuration_uid:
            configuration = self.configuration_repository.read_id(self.current_configuration_uid)
            return configuration["name"]

        return None

    def get_current_configuration_part_number(self):
        if self.current_configuration_uid:
            configuration = self.configuration_repository.read_id(self.current_configuration_uid)
            return configuration["part_number"]

        return None
