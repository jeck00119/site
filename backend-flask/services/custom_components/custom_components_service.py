import numpy as np

from services.algorithms.basic.basic_algorithms_service import BasicAlgorithmsService
from services.algorithms.basic.models.data_representation import NumpyType
from services.base.enhanced_base_service import EnhancedBaseService
from services.custom_components.custom_components_model import CustomComponentModel
from services.image_source.image_source_service import ImageSourceService
from services.services_exceptions import NoLiveAlgSet, NoLiveFrameSet
from src.utils import frame_to_base64


class CustomComponentsService(EnhancedBaseService):
    def __init__(self):
        # Initialize EnhancedBaseService (combines BaseService + EntityManagerMixin)
        super().__init__(entity_type='custom_components', model_class=CustomComponentModel)
    
    def _load_service_dependencies(self) -> None:
        """Load service dependencies - called automatically by EnhancedBaseService."""
        if not self.get_service_dependency('image_source'):
            self.add_service_dependency('image_source', ImageSourceService())
        if not self.get_service_dependency('algorithms'):
            self.add_service_dependency('algorithms', BasicAlgorithmsService())
    
    # Properties for backward compatibility
    @property
    def image_source_service(self):
        """Legacy property for backward compatibility."""
        return self.get_service_dependency('image_source')
    
    @property
    def algorithm_service(self):
        """Legacy property for backward compatibility."""
        return self.get_service_dependency('algorithms')
    
    @property
    def components(self) -> dict[str, CustomComponentModel]:
        """Legacy property for backward compatibility."""
        return self._entities

    # Use EnhancedBaseService methods with backward-compatible wrappers
    def post_component(self, component: CustomComponentModel):
        """Legacy method - use enhanced base service functionality."""
        self.post_entity(component)

    def patch_component(self, component: CustomComponentModel):
        """Legacy method - use enhanced base service functionality."""
        self.patch_entity(component)

    def delete_component(self, uid: str):
        """Legacy method - use enhanced base service functionality."""
        self.delete_entity_by_uid(uid)

    # EnhancedBaseService handles all initialization automatically

    def process_component(self, uid):
        """Process a custom component using EntityManagerMixin methods."""
        component = self.get_entity(uid)
        if not component:
            self.logger.error(f"Custom component {uid} not found for processing")
            raise ValueError(f"Custom component {uid} not found")
            
        try:
            alg = self.algorithm_service.get_live_algorithm()
            frame = self.image_source_service.grab_from_image_source(component.image_source_uid)
            result = alg.execute(frame)
            
            self.logger.debug(f"Processed custom component {uid} successfully")
            return result
        except Exception as e:
            self.logger.error(f"Failed to process custom component {uid}: {e}")
            raise

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
