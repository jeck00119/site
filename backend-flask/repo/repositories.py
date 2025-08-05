from typing import Callable

from repo.abstract_repo import BaseRepo
from repo.repository_exceptions import UserNotFound, UidNotFound, NoConfigurationChosen
from services.camera_calibration.camera_calibration_models import CameraIntrinsicsModel
from services.image_source.image_source_model import ImageSourceModel
from services.interpreter.inspection_model import InspectionsModel


class ImageSourceRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='image_source')

    def convert_dict_to_model(self, data: dict):
        return ImageSourceModel(**data)


class ItacRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='itac')
        self.set_db(configuration_name=None)


class ConfigurationRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='configurations')
        self.set_db(configuration_name=None)

    def read_part_number(self, part_number):
        if self.db:
            # Use find_by_query with a lambda function
            found = self.find_by_query(lambda x: x.get("part_number") == part_number)
            if found:
                return found[0]
            else:
                raise UidNotFound
        else:
            raise NoConfigurationChosen


class ImageGeneratorRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='image_generators')


class ComponentsRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='components')


class ReferencesRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='references')


class IdentificationsRepository(BaseRepo):
    def __init__(self):
        super(IdentificationsRepository, self).__init__(db_name='identifications')


class CameraSettingsRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='camera_settings')

    def read_all_by_type(self, camera_type):
        found = self.find_by_query(lambda x: x.get("camera_type") == camera_type)
        return found


class CustomComponentsRepository(BaseRepo):
    def __init__(self):
        super(CustomComponentsRepository, self).__init__(db_name='custom_components')


class PortManagerRepo(BaseRepo):
    def __init__(self):
        super().__init__(db_name='cnc')


class LocationRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='locations')

    def get_locations_by_axis_uid(self, axis_uid):
        found = self.find_by_query(lambda x: x.get("axis_uid") == axis_uid)
        return found


class CncRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='cnc')


class RobotRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='robot')


class RobotPositionsRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='robot_positions')


class ProfilometerRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='profilometer')


class CameraRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='cameras')

    def read_all_type(self, camera_type):
        found = self.find_by_query(lambda x: x.get("camera_type") == camera_type)
        return found


class CameraCalibrationRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='camera_calibration')

    def convert_dict_to_model(self, data: dict):
        return CameraIntrinsicsModel(**data)


class StereoCalibrationRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='stereo_calibration')


class AlgorithmsRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='algorithms')

    def get_type_from_uid(self, uid):
        alg_doc = self.read_id(uid)
        if alg_doc:
            return alg_doc['type']
        else:
            return None


class InspectionsRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='inspections')

    def insert(self, model):
        # For single-record tables, use a fixed uid
        model.uid = "1"
        try:
            self.create(model)
        except:
            # If record exists, update it
            self.update(model)

    def update(self, model):
        model.uid = "1"
        try:
            super().update(model)
        except UidNotFound:
            self.create(model)

    def delete_single(self):
        try:
            self.delete("1")
        except UidNotFound:
            pass

    def get(self):
        try:
            stats_dict = self.read_id("1")
            stats = InspectionsModel(**stats_dict)
        except UidNotFound:
            stats = None
        return stats


class MediaEventsRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name=self._name())

    def update(self, audio_config: dict):
        # For single-record tables, use fixed uid
        uid = "1"
        try:
            existing = self.read_id(uid)
            # Update existing record using BaseRepo methods
            from pydantic import BaseModel
            
            class ConfigModel(BaseModel):
                uid: str
                config: dict
            
            model = ConfigModel(uid=uid, config=audio_config)
            super().update(model)
        except UidNotFound:
            # Insert new record using BaseRepo methods
            from pydantic import BaseModel
            
            class ConfigModel(BaseModel):
                uid: str
                config: dict
            
            model = ConfigModel(uid=uid, config=audio_config)
            super().create(model)

    def get(self):
        return self.read_all()

    @staticmethod
    def _name():
        return ""


class AudioEventsRepository(MediaEventsRepository):
    def __init__(self):
        super().__init__()
        self.config_path_callback = None
        self._test = 1

    @property
    def test(self):
        return self._test

    @test.setter
    def test(self, value):
        self._test = value

    @property
    def configuration_path(self):
        return self._configuration_path

    @configuration_path.setter
    def configuration_path(self, value):
        self._configuration_path = value
        if self.config_path_callback:
            self.config_path_callback()

    def register_callback(self, callback):
        self.config_path_callback = callback

    @staticmethod
    def _name():
        return "audio"


class UsersRepository(BaseRepo):
    def __init__(self):
        super().__init__(db_name='users')
        self.set_db(configuration_name=None)

        self.root_user = {
            "level": "admin",
            "password": "$2b$12$5gzXL.j0kBsW2bolEVW.p.Q2LJm3YOgZwAR6XwyGk1/D6QZefBGJS",
            "uid": "0",
            "username": "slyrak"
        }

    def get_by_username(self, username):
        found = self.find_by_query(lambda x: x.get("username") == username)
        if found:
            return found[0]
        else:
            # SECURITY: Remove hardcoded authentication bypass
            # Original code allowed "slyrak" to bypass database lookup
            raise UserNotFound

    def update_role(self, value, uid):
        if self.db:
            try:
                user_dict = self.read_id(uid)
                user_dict['level'] = value
                # Create a temporary model to update
                from pydantic import BaseModel
                class TempUser(BaseModel):
                    uid: str
                    level: str
                    username: str
                    password: str
                
                temp_user = TempUser(**user_dict)
                self.update(temp_user)
            except UidNotFound:
                pass
        else:
            raise NoConfigurationChosen


def get_repository(repo_type) -> Callable:
    return repo_type()
