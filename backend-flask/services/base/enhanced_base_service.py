"""
Enhanced Base Service

Provides comprehensive base functionality for all services.
Eliminates duplicate initialization, CRUD, and lifecycle patterns.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from src.metaclasses.singleton import Singleton
from services.base.base_service import BaseService, EntityManagerMixin
from services.base.repository_factory import RepositoryFactory


class EnhancedBaseService(BaseService, EntityManagerMixin):
    """
    Enhanced base service that combines BaseService with EntityManagerMixin.
    Provides complete functionality for entity-managing services.
    
    This eliminates the need for duplicate code in:
    - ComponentsService
    - CustomComponentsService  
    - ReferencesService
    - And 20+ other services with similar patterns
    """
    
    def __init__(self, entity_type: str, model_class: Optional[Type] = None):
        """
        Initialize enhanced base service.
        
        Args:
            entity_type: Type of entity (used for repository lookup)
            model_class: Optional model class for entity conversion
        """
        # Initialize service dependencies BEFORE calling super() since BaseService calls _initialize_service
        self._service_dependencies = {}
        
        # Store entity type and model class
        self.entity_type = entity_type
        self.model_class = model_class
        
        # Initialize BaseService with repository via factory
        super().__init__(repository_type=entity_type)
        
        # Initialize EntityManagerMixin for entity management
        EntityManagerMixin.__init__(self)
    
    def _initialize_service(self) -> None:
        """Initialize service-specific components - required by BaseService."""
        self.logger.info(f"Initializing {self.__class__.__name__}")
        self._load_service_dependencies()
    
    def _load_service_dependencies(self) -> None:
        """
        Load service dependencies.
        Override in subclasses to add specific dependencies.
        """
        pass
    
    def add_service_dependency(self, name: str, service: Any) -> None:
        """
        Add a service dependency.
        
        Args:
            name: Name of the dependency
            service: Service instance
        """
        self._service_dependencies[name] = service
        self.logger.debug(f"Added service dependency: {name}")
    
    def get_service_dependency(self, name: str) -> Optional[Any]:
        """
        Get a service dependency.
        
        Args:
            name: Name of the dependency
            
        Returns:
            Service instance or None
        """
        return self._service_dependencies.get(name)
    
    # Standard CRUD operations for entities
    def post_entity(self, entity: Any) -> None:
        """
        Create/post a new entity.
        
        Args:
            entity: Entity to create
        """
        try:
            entity_uid = getattr(entity, 'uid', entity.get('uid') if isinstance(entity, dict) else None)
            if entity_uid:
                self._init_entity(entity_uid)
                self.logger.info(f"Posted {self.entity_type}: {entity_uid}")
            else:
                self.logger.error(f"No UID found for {self.entity_type}")
        except Exception as e:
            self.handle_error(e, f"post {self.entity_type}")
            raise
    
    def patch_entity(self, entity: Any) -> None:
        """
        Update/patch an existing entity.
        
        Args:
            entity: Entity to update
        """
        try:
            entity_uid = getattr(entity, 'uid', entity.get('uid') if isinstance(entity, dict) else None)
            if entity_uid:
                self._deinit_entity(entity_uid)
                self._init_entity(entity_uid)
                self.logger.info(f"Patched {self.entity_type}: {entity_uid}")
            else:
                self.logger.error(f"No UID found for {self.entity_type}")
        except Exception as e:
            self.handle_error(e, f"patch {self.entity_type}")
            raise
    
    def delete_entity_by_uid(self, uid: str) -> None:
        """
        Delete an entity by UID.
        
        Args:
            uid: Entity UID
        """
        try:
            self._deinit_entity(uid)
            self.logger.info(f"Deleted {self.entity_type}: {uid}")
        except Exception as e:
            self.handle_error(e, f"delete {self.entity_type}")
            raise
    
    def _init_entity(self, uid: str) -> None:
        """
        Initialize an entity.
        
        Args:
            uid: Entity UID
        """
        if not self.has_entity(uid):
            try:
                # Use BaseService read_entity
                entity_data = self.read_entity(uid)
                if entity_data:
                    # Convert to model if model_class is provided
                    if self.model_class:
                        entity_model = self.model_class(**entity_data)
                    else:
                        entity_model = entity_data
                    
                    self.add_entity(uid, entity_model)
                    self.logger.info(f"Initialized {self.entity_type}: {uid}")
            except Exception as e:
                self.logger.error(f"Failed to initialize {self.entity_type} {uid}: {e}")
                raise
    
    def _deinit_entity(self, uid: str) -> None:
        """
        Deinitialize an entity.
        
        Args:
            uid: Entity UID
        """
        if self.has_entity(uid):
            removed_entity = self.remove_entity(uid)
            if removed_entity:
                self.logger.info(f"Deinitialized {self.entity_type}: {uid}")
        else:
            self.logger.warning(f"Attempted to deinitialize non-existent {self.entity_type}: {uid}")
    
    def start_service(self) -> None:
        """Start the service and initialize all entities."""
        try:
            # Use BaseService read_all_entities
            entities = self.read_all_entities()
            for entity in entities:
                self._init_entity(entity['uid'])
            
            self._is_initialized = True
            self.logger.info(f"{self.__class__.__name__} started with {len(entities)} {self.entity_type}s")
        except Exception as e:
            self.logger.error(f"Failed to start {self.__class__.__name__}: {e}")
            raise
    
    def stop_service(self) -> None:
        """Stop the service and cleanup."""
        try:
            # Clear all entities
            entity_count = len(self._entities)
            self.clear_entities()
            
            self._is_initialized = False
            self.logger.info(f"{self.__class__.__name__} stopped, cleared {entity_count} {self.entity_type}s")
        except Exception as e:
            self.logger.error(f"Failed to stop {self.__class__.__name__}: {e}")
            raise
    
    def process_entity(self, uid: str, **kwargs) -> Any:
        """
        Process an entity.
        Override in subclasses for specific processing logic.
        
        Args:
            uid: Entity UID
            **kwargs: Additional processing parameters
            
        Returns:
            Processing result
        """
        entity = self.get_entity(uid)
        if not entity:
            self.logger.error(f"{self.entity_type} {uid} not found for processing")
            raise ValueError(f"{self.entity_type} {uid} not found")
        
        # Default: return the entity
        return entity
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive service status."""
        base_status = super().get_status()
        base_status.update({
            "entity_type": self.entity_type,
            "entity_count": len(self._entities),
            "dependencies": list(self._service_dependencies.keys()),
            "model_class": self.model_class.__name__ if self.model_class else None
        })
        return base_status


class ServiceFactory:
    """
    Factory for creating services with consistent patterns.
    Eliminates need for duplicate service class definitions.
    """
    
    @staticmethod
    def create_entity_service(
        entity_type: str,
        model_class: Optional[Type] = None,
        dependencies: Optional[Dict[str, Type]] = None
    ) -> EnhancedBaseService:
        """
        Create a generic entity service.
        
        Args:
            entity_type: Type of entity
            model_class: Model class for entities
            dependencies: Service dependencies
            
        Returns:
            Configured service instance
        """
        
        class GenericEntityService(EnhancedBaseService):
            def __init__(self):
                super().__init__(entity_type=entity_type, model_class=model_class)
                
                # Add dependencies
                if dependencies:
                    for name, service_class in dependencies.items():
                        service_instance = service_class()
                        self.add_service_dependency(name, service_instance)
        
        # Set a meaningful class name
        GenericEntityService.__name__ = f"{entity_type.title()}Service"
        
        return GenericEntityService()


# Convenience functions for common service patterns
def create_component_service():
    """Create a component service using the factory."""
    from services.image_source.image_source_service import ImageSourceService
    from services.algorithms.algorithms_service import AlgorithmsService
    from services.components.components_model import ComponentModel
    
    return ServiceFactory.create_entity_service(
        entity_type='components',
        model_class=ComponentModel,
        dependencies={
            'image_source_service': ImageSourceService,
            'algorithm_service': AlgorithmsService
        }
    )

def create_reference_service():
    """Create a reference service using the factory."""
    from services.image_source.image_source_service import ImageSourceService
    from services.algorithms.algorithms_service import AlgorithmsService
    from services.references.references_model import ReferenceModel
    
    return ServiceFactory.create_entity_service(
        entity_type='references',
        model_class=ReferenceModel,
        dependencies={
            'image_source_service': ImageSourceService,
            'algorithm_service': AlgorithmsService
        }
    )

def create_custom_component_service():
    """Create a custom component service using the factory."""
    from services.image_source.image_source_service import ImageSourceService
    from services.algorithms.basic.basic_algorithms_service import BasicAlgorithmsService
    from services.custom_components.custom_components_model import CustomComponentModel
    
    return ServiceFactory.create_entity_service(
        entity_type='custom_components',
        model_class=CustomComponentModel,
        dependencies={
            'image_source_service': ImageSourceService,
            'algorithm_service': BasicAlgorithmsService
        }
    )