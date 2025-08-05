import json

from repo.repositories import AlgorithmsRepository, ReferencesRepository
from services.algorithms.algorithms_factory import AlgorithmFactory
from services.algorithms.algorithms_models import AlgorithmModel, EnumAlgorithmType, EnumReferenceAlgorithmType
from services.algorithms.models_factory import ModelsFactory
from services.algorithms.reference_algorithms_factory import ReferenceAlgorithmFactory
from services.image_source.image_source_service import ImageSourceService
from services.references.references_model import ReferenceModel
from services.services_exceptions import NoLiveAlgSet
from src.metaclasses.singleton import Singleton


class AlgorithmsService(metaclass=Singleton):
    def __init__(self):
        self.algorithms_repository = AlgorithmsRepository()
        self.references_repository = ReferencesRepository()
        self.image_source_service = ImageSourceService()
        self.live_algorithm = None
        self.reference_algorithm = None

    def set_live_algorithm(self, algorithm_type):
        model = self.get_model_from_type(algorithm_type)
        self.live_algorithm = AlgorithmFactory.create_algorithm(algorithm_type, model.model_dump())

    def set_reference_algorithm(self, algorithm_type):
        model = self.get_reference_model_from_type(algorithm_type)
        self.reference_algorithm = ReferenceAlgorithmFactory.create_algorithm(algorithm_type, model.model_dump())

    def set_reference_algorithm_from_dict(self, alg_type, alg_parameters):
        self.reference_algorithm = ReferenceAlgorithmFactory.create_algorithm(alg_type, alg_parameters)

    def reset_reference_algorithm(self):
        self.reference_algorithm = None

    def set_live_algorithm_reference(self):
        if self.live_algorithm:
            self.live_algorithm.set_reference_algorithm(self.reference_algorithm)

    def execute_algorithm(self, uid, frame):
        alg_model = AlgorithmModel(**self.algorithms_repository.read_id(uid))
        alg_obj = AlgorithmFactory.create_algorithm(alg_model.type, alg_model.parameters)
        return alg_obj.execute(frame)

    def process_algorithm(self, algorithm, image_source_uid):
        frame = self.image_source_service.grab_from_image_source(uid=image_source_uid)
        result = algorithm.execute(frame)

        return result

    def set_live_algorithm_reference_repo(self, reference_uid):
        if self.live_algorithm:
            reference_dict = self.references_repository.read_id(reference_uid)

            if reference_dict:
                reference_model = ReferenceModel(**reference_dict)
                algorithm_dict = self.algorithms_repository.read_id(reference_model.algorithm_uid)

                if algorithm_dict:
                    algorithm_model = AlgorithmModel(**algorithm_dict)
                    reference_algorithm = ReferenceAlgorithmFactory.create_algorithm(algorithm_model.type,
                                                                                     algorithm_model.parameters)
                    self.live_algorithm.set_reference_algorithm(reference_algorithm)

    def set_live_algorithm_reference_dict(self, alg_type, alg_parameters):
        reference_algorithm = ReferenceAlgorithmFactory.create_algorithm(alg_type, alg_parameters)
        if self.live_algorithm:
            self.live_algorithm.set_reference_algorithm(reference_algorithm)

    def get_live_algorithm(self):
        if self.live_algorithm is None:
            raise NoLiveAlgSet

        return self.live_algorithm

    def get_reference_algorithm(self):
        if not self.reference_algorithm:
            raise NoLiveAlgSet

        return self.reference_algorithm

    def edit_live_algorithm(self, key, val):
        if self.live_algorithm is not None:
            self.live_algorithm.__setattr__(key, val)
        else:
            raise NoLiveAlgSet

    def edit_reference_algorithm(self, key, val):
        if self.reference_algorithm:
            self.reference_algorithm.__setattr__(key, val)
        else:
            raise NoLiveAlgSet

    def create_algorithm(self, uid):
        alg_model = AlgorithmModel(**self.algorithms_repository.read_id(uid))
        algorithm = AlgorithmFactory.create_algorithm(alg_model.type, alg_model.parameters)
        return algorithm

    @staticmethod
    def get_model_from_type(algorithm_type):
        return ModelsFactory.create_model(algorithm_type)

    @staticmethod
    def get_reference_model_from_type(algorithm_type):
        return ModelsFactory.create_model(algorithm_type)

    @staticmethod
    def load_ui_dictionary(file_name):
        with open(file_name) as f:
            data = json.load(f)

        return data

    @staticmethod
    def get_ui_from_type(algorithm_type):
        model = ModelsFactory.create_model(algorithm_type)
        return model.get_ui_from_type()

    @staticmethod
    def get_ui_from_reference_type(algorithm_type):
        model = ModelsFactory.create_model(algorithm_type)
        return model.get_ui_from_type()

    @staticmethod
    def list_algorithms_types():
        return EnumAlgorithmType.list()

    @staticmethod
    def list_reference_algorithms_types():
        return EnumReferenceAlgorithmType.list()
