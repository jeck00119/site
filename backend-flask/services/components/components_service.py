from services.algorithms.algorithms_service import AlgorithmsService
from services.base.enhanced_base_service import EnhancedBaseService
from services.components.components_model import ComponentModel
from services.image_source.image_source_service import ImageSourceService


class ComponentsService(EnhancedBaseService):
    def __init__(self):
        # Initialize EnhancedBaseService (combines BaseService + EntityManagerMixin)
        super().__init__(entity_type='components', model_class=ComponentModel)
    
    def _load_service_dependencies(self) -> None:
        """Load service dependencies - called automatically by EnhancedBaseService."""
        if not self.get_service_dependency('image_source'):
            self.add_service_dependency('image_source', ImageSourceService())
        if not self.get_service_dependency('algorithms'):
            self.add_service_dependency('algorithms', AlgorithmsService())
    
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
    def components(self) -> dict[str, ComponentModel]:
        """Legacy property for backward compatibility."""
        return self._entities

    # Use EnhancedBaseService methods with backward-compatible wrappers
    def post_component(self, component: ComponentModel):
        """Legacy method - use enhanced base service functionality."""
        self.post_entity(component)

    def patch_component(self, component: ComponentModel):
        """Legacy method - use enhanced base service functionality."""
        self.patch_entity(component)

    def delete_component(self, uid: str):
        """Legacy method - use enhanced base service functionality."""
        self.delete_entity_by_uid(uid)

    # EnhancedBaseService handles start_service automatically, no need to override

    def process_component(self, uid):
        """Process a component using EntityManagerMixin methods."""
        processed_component: ComponentModel = self.get_entity(uid)
        if not processed_component:
            self.logger.error(f"Component {uid} not found for processing")
            raise ValueError(f"Component {uid} not found")
            
        try:
            frame = self.image_source_service.grab_from_image_source(uid=processed_component.image_source_uid)
            result = self.algorithm_service.execute_algorithm(uid=processed_component.algorithm_uid, frame=frame)
            
            self.logger.debug(f"Processed component {uid} successfully")
            return result
        except Exception as e:
            self.logger.error(f"Failed to process component {uid}: {e}")
            raise

    # _init_entity and _deinit_entity are now handled by EnhancedBaseService automatically


