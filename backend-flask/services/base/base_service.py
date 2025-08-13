"""
Base Service Class

Provides common functionality for all service classes to eliminate code duplication.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from src.metaclasses.singleton import Singleton
from services.base.repository_factory import RepositoryFactory

# Type variable for repository types
T = TypeVar('T')


class SingletonABCMeta(type(ABC), type(Singleton)):
    """
    Metaclass that combines ABC and Singleton metaclasses.
    """
    pass


class BaseService(ABC, metaclass=SingletonABCMeta):
    """
    Abstract base class for all services.
    
    Provides common functionality:
    - Logging setup
    - Repository management
    - Error handling
    - CRUD operations
    - Initialization patterns
    """
    
    def __init__(self, repository_class: Optional[Type] = None, repository_type: Optional[str] = None):
        """
        Initialize base service.
        
        Args:
            repository_class: Repository class to initialize (optional, for backward compatibility)
            repository_type: Repository type for RepositoryFactory (preferred method)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._is_initialized = False
        self._repository = None
        
        # Initialize repository using factory or class
        if repository_type:
            self._repository = RepositoryFactory.get_repository(repository_type, singleton=True)
            self.logger.debug(f"Initialized repository via factory: {repository_type}")
        elif repository_class:
            # Fallback to direct instantiation for backward compatibility
            self._repository = repository_class()
            self.logger.debug(f"Initialized repository via class: {repository_class.__name__}")
            
        # Initialize service-specific components
        self._initialize_service()
    
    @abstractmethod
    def _initialize_service(self) -> None:
        """
        Initialize service-specific components.
        Must be implemented by subclasses.
        """
        pass
    
    def get_repository(self):
        """Get the service repository."""
        return self._repository
    
    def set_repository(self, repository):
        """Set the service repository."""
        self._repository = repository
    
    # Common CRUD operations
    def create_entity(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new entity.
        
        Args:
            entity_data: Entity data dictionary
            
        Returns:
            Created entity data
        """
        try:
            if not self._repository:
                raise ValueError("Repository not initialized")
                
            result = self._repository.create(entity_data)
            self.logger.info(f"Created entity with ID: {entity_data.get('uid', 'unknown')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create entity: {e}")
            raise
    
    def read_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Read an entity by ID.
        
        Args:
            entity_id: Entity unique identifier
            
        Returns:
            Entity data or None if not found
        """
        try:
            if not self._repository:
                raise ValueError("Repository not initialized")
                
            result = self._repository.read_id(entity_id)
            if result:
                self.logger.debug(f"Retrieved entity: {entity_id}")
            else:
                self.logger.warning(f"Entity not found: {entity_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to read entity {entity_id}: {e}")
            raise
    
    def read_all_entities(self) -> List[Dict[str, Any]]:
        """
        Read all entities.
        
        Returns:
            List of all entities
        """
        try:
            if not self._repository:
                raise ValueError("Repository not initialized")
                
            result = self._repository.read_all()
            self.logger.debug(f"Retrieved {len(result)} entities")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to read all entities: {e}")
            raise
    
    def update_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an entity.
        
        Args:
            entity_id: Entity unique identifier
            entity_data: Updated entity data
            
        Returns:
            Updated entity data
        """
        try:
            if not self._repository:
                raise ValueError("Repository not initialized")
                
            result = self._repository.update(entity_id, entity_data)
            self.logger.info(f"Updated entity: {entity_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update entity {entity_id}: {e}")
            raise
    
    def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity.
        
        Args:
            entity_id: Entity unique identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            if not self._repository:
                raise ValueError("Repository not initialized")
                
            result = self._repository.delete(entity_id)
            self.logger.info(f"Deleted entity: {entity_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to delete entity {entity_id}: {e}")
            raise
    
    # Common initialization patterns
    def initialize_all(self) -> None:
        """
        Initialize all entities from repository.
        Override in subclasses for specific initialization logic.
        """
        try:
            entities = self.read_all_entities()
            for entity in entities:
                entity_id = entity.get('uid')
                if entity_id:
                    self._initialize_entity(entity_id)
            
            self._is_initialized = True
            self.logger.info(f"Initialized {len(entities)} entities")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize all entities: {e}")
            raise
    
    def _initialize_entity(self, entity_id: str) -> Any:
        """
        Initialize a specific entity.
        Override in subclasses for specific initialization logic.
        
        Args:
            entity_id: Entity unique identifier
            
        Returns:
            Initialized entity or result
        """
        # Default implementation - just log
        self.logger.debug(f"Initializing entity: {entity_id}")
        return None
    
    def _deinitialize_entity(self, entity_id: str) -> None:
        """
        Deinitialize a specific entity.
        Override in subclasses for specific cleanup logic.
        
        Args:
            entity_id: Entity unique identifier
        """
        # Default implementation - just log
        self.logger.debug(f"Deinitializing entity: {entity_id}")
    
    # Common error handling
    def handle_error(self, error: Exception, context: str = "") -> str:
        """
        Handle and log errors consistently.
        
        Args:
            error: Exception that occurred
            context: Additional context information
            
        Returns:
            Error message string
        """
        error_msg = f"{context}: {str(error)}" if context else str(error)
        self.logger.error(error_msg)
        return error_msg
    
    # Service lifecycle methods
    def start_service(self) -> None:
        """
        Start the service.
        Override in subclasses for specific startup logic.
        """
        try:
            if not self._is_initialized:
                self.initialize_all()
            self.logger.info(f"{self.__class__.__name__} started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start {self.__class__.__name__}: {e}")
            raise
    
    def stop_service(self) -> None:
        """
        Stop the service.
        Override in subclasses for specific cleanup logic.
        """
        try:
            self._is_initialized = False
            self.logger.info(f"{self.__class__.__name__} stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to stop {self.__class__.__name__}: {e}")
            raise
    
    def restart_service(self) -> None:
        """
        Restart the service.
        """
        self.stop_service()
        self.start_service()
    
    @property
    def is_initialized(self) -> bool:
        """Check if service is initialized."""
        return self._is_initialized
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get service status information.
        
        Returns:
            Service status dictionary
        """
        return {
            "service_name": self.__class__.__name__,
            "is_initialized": self._is_initialized,
            "has_repository": self._repository is not None,
            "repository_type": self._repository.__class__.__name__ if self._repository else None
        }


class EntityManagerMixin:
    """
    Mixin for services that manage collections of entities (like cameras, robots, etc.).
    """
    
    def __init__(self):
        self._entities: Dict[str, Any] = {}
    
    def add_entity(self, entity_id: str, entity: Any) -> None:
        """Add an entity to the managed collection."""
        self._entities[entity_id] = entity
        if hasattr(self, 'logger'):
            self.logger.debug(f"Added entity to collection: {entity_id}")
    
    def remove_entity(self, entity_id: str) -> Optional[Any]:
        """Remove an entity from the managed collection."""
        entity = self._entities.pop(entity_id, None)
        if hasattr(self, 'logger'):
            if entity:
                self.logger.debug(f"Removed entity from collection: {entity_id}")
            else:
                self.logger.warning(f"Entity not found in collection: {entity_id}")
        return entity
    
    def get_entity(self, entity_id: str) -> Optional[Any]:
        """Get an entity from the managed collection."""
        return self._entities.get(entity_id)
    
    def get_all_entities(self) -> Dict[str, Any]:
        """Get all entities in the managed collection."""
        return self._entities.copy()
    
    def has_entity(self, entity_id: str) -> bool:
        """Check if an entity exists in the managed collection."""
        return entity_id in self._entities
    
    def clear_entities(self) -> None:
        """Clear all entities from the managed collection."""
        count = len(self._entities)
        self._entities.clear()
        if hasattr(self, 'logger'):
            self.logger.info(f"Cleared {count} entities from collection")


class ConfigurableServiceMixin:
    """
    Mixin for services that need configuration management.
    """
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """Set service configuration."""
        self._config.update(config)
        if hasattr(self, 'logger'):
            self.logger.debug(f"Updated configuration with {len(config)} settings")
    
    def get_config(self, key: str = None, default: Any = None) -> Any:
        """Get configuration value(s)."""
        if key is None:
            return self._config.copy()
        return self._config.get(key, default)
    
    def has_config(self, key: str) -> bool:
        """Check if configuration key exists."""
        return key in self._config

