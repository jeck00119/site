from repo.repositories import ComponentsRepository
from services.algorithms.algorithms_service import AlgorithmsService
from services.components.components_model import ComponentModel
from services.image_source.image_source_service import ImageSourceService
from src.metaclasses.singleton import Singleton


class ComponentsService(metaclass=Singleton):
    def __init__(self):
        self.components: dict[str:ComponentModel] = {}
        self.components_repository = ComponentsRepository()
        self.image_source_service = ImageSourceService()
        self.algorithm_service = AlgorithmsService()

    def post_component(self, component:ComponentModel):
        self._init_component(component.uid)

    def patch_component(self, component:ComponentModel):
        self._deinit_component(component.uid)
        self._init_component(component.uid)

    def delete_component(self, uid):
        self._deinit_component(uid)

    def start_service(self):
        for component in self.components_repository.read_all():
            self._init_component(component['uid'])

    def process_component(self, uid):
        processed_component: ComponentModel = self.components[uid]
        frame = self.image_source_service.grab_from_image_source(uid=processed_component.image_source_uid)
        result = self.algorithm_service.execute_algorithm(uid=processed_component.algorithm_uid, frame=frame)

        return result

    def _init_component(self, uid):
        if uid not in self.components.keys():
            component_model = ComponentModel(**self.components_repository.read_id(uid))
            self.components[uid] = component_model

    def _deinit_component(self, uid):
        if uid not in self.components.keys():
            return
        self.components.pop(uid)


