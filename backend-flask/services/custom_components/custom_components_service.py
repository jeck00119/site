import numpy as np

from repo.repositories import CustomComponentsRepository
from services.algorithms.basic.basic_algorithms_service import BasicAlgorithmsService
from services.algorithms.basic.models.data_representation import NumpyType
from services.custom_components.custom_components_model import CustomComponentModel
from services.image_source.image_source_service import ImageSourceService
from services.services_exceptions import NoLiveAlgSet, NoLiveFrameSet
from src.metaclasses.singleton import Singleton
from src.utils import frame_to_base64


class CustomComponentsService(metaclass=Singleton):
    def __init__(self):
        self.components: dict[str:CustomComponentModel] = {}
        self.components_repository = CustomComponentsRepository()
        self.image_source_service = ImageSourceService()
        self.algorithm_service = BasicAlgorithmsService()

    def post_component(self, component: CustomComponentModel):
        self._init_component(component.uid)

    def patch_component(self, component: CustomComponentModel):
        self._deinit_component(component.uid)
        self._init_component(component.uid)

    def delete_component(self, uid):
        self._deinit_component(uid)

    def start_service(self):
        for component in self.components_repository.read_all():
            self._init_component(component['uid'])

    def _init_component(self, uid):
        if uid not in self.components.keys():
            component_model = CustomComponentModel(**self.components_repository.read_id(uid))
            self.components[uid] = component_model

    def _deinit_component(self, uid):
        if uid not in self.components.keys():
            return
        self.components.pop(uid)

    def process_component(self, uid):
        alg = self.algorithm_service.get_live_algorithm()
        frame = self.image_source_service.grab_from_image_source(self.components[uid].image_source_uid)
        alg.execute(frame)

    def process_live_component(self, image_source_uid):
        if self.algorithm_service.live_algorithm is None:
            raise NoLiveAlgSet
        if image_source_uid not in self.image_source_service.images_sources_last_frame.keys():
            raise NoLiveFrameSet

        live_alg = self.algorithm_service.get_live_algorithm()
        frame = self.image_source_service.images_sources_last_frame[image_source_uid]
        self.algorithm_service.set_input_frame(frame)
        result = live_alg.execute()

        out_image = None

        results = []

        compound_block = self.algorithm_service.get_compound_block()

        if compound_block:
            for block_idx, block in enumerate(compound_block):

                data = {
                    'inputs': [],
                    'outputs': []
                }

                for alg_input in block.ins:
                    if isinstance(alg_input, NumpyType):
                        val = alg_input.value()
                    else:
                        val = np.zeros(shape=(128, 128), dtype=np.uint8)
                    data['inputs'].append(frame_to_base64(val))

                for i, alg_output in enumerate(block.outs):
                    if isinstance(alg_output, NumpyType):
                        val = alg_output.value()
                    else:
                        val = np.zeros(shape=(128, 128), dtype=np.uint8)
                    data['outputs'].append(frame_to_base64(val))

                results.append(data)

        if isinstance(result.outs[0], NumpyType):
            out_image = result.outs[0].value()
        else:
            out_image = np.zeros(shape=(128, 128), dtype=np.uint8)

        return out_image, results
