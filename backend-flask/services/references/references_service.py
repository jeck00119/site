from repo.repositories import ReferencesRepository
from services.algorithms.algorithms_service import AlgorithmsService
from services.image_source.image_source_service import ImageSourceService
from services.references.references_model import ReferenceModel
from src.metaclasses.singleton import Singleton


class ReferencesService(metaclass=Singleton):
    def __init__(self):
        self.references: dict[str: ReferenceModel] = {}
        self.references_repository = ReferencesRepository()
        self.image_source_service = ImageSourceService()
        self.algorithm_service = AlgorithmsService()

    def post_reference(self, reference: ReferenceModel):
        self._init_reference(reference.uid)

    def patch_reference(self, reference: ReferenceModel):
        self._deinit_reference(reference.uid)
        self._init_reference(reference.uid)

    def delete_reference(self, uid):
        self._deinit_reference(uid)

    def start_service(self):
        for reference in self.references_repository.read_all():
            self._init_reference(reference['uid'])

    def _init_reference(self, uid):
        if uid not in self.references.keys():
            reference_model = ReferenceModel(**self.references_repository.read_id(uid))
            self.references[uid] = reference_model

    def _deinit_reference(self, uid):
        if uid not in self.references.keys():
            return
        self.references.pop(uid)
