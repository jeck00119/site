from services.algorithms.algorithms_service import AlgorithmsService
from services.base.enhanced_base_service import EnhancedBaseService
from services.image_source.image_source_service import ImageSourceService
from services.references.references_model import ReferenceModel


class ReferencesService(EnhancedBaseService):
    def __init__(self):
        # Initialize EnhancedBaseService (combines BaseService + EntityManagerMixin)
        super().__init__(entity_type='references', model_class=ReferenceModel)
    
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
    def references(self) -> dict[str, ReferenceModel]:
        """Legacy property for backward compatibility."""
        return self._entities

    # Use EnhancedBaseService methods with backward-compatible wrappers
    def post_reference(self, reference: ReferenceModel):
        """Legacy method - use enhanced base service functionality."""
        self.post_entity(reference)

    def patch_reference(self, reference: ReferenceModel):
        """Legacy method - use enhanced base service functionality."""
        self.patch_entity(reference)

    def delete_reference(self, uid: str):
        """Legacy method - use enhanced base service functionality."""
        self.delete_entity_by_uid(uid)

    # EnhancedBaseService handles all initialization automatically
