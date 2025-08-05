"""
Repository Factory

Centralizes repository creation and management to eliminate duplication.
"""

import logging
from typing import Dict, Type, Any, Optional
from repo.repositories import (
    CameraRepository, CameraSettingsRepository,
    ComponentsRepository, CustomComponentsRepository,
    CncRepository, LocationRepository,
    RobotRepository, AlgorithmsRepository,
    ReferencesRepository, UsersRepository,
    ConfigurationRepository, ImageSourceRepository,
    CameraCalibrationRepository, ImageGeneratorRepository
)


class RepositoryFactory:
    """
    Factory class for creating and managing repository instances.
    """
    
    # Repository type mapping
    REPOSITORY_TYPES = {
        'camera': CameraRepository,
        'camera_settings': CameraSettingsRepository,
        'components': ComponentsRepository,
        'custom_components': CustomComponentsRepository,
        'cnc': CncRepository,
        'location': LocationRepository,
        'robot': RobotRepository,
        'algorithms': AlgorithmsRepository,
        'references': ReferencesRepository,
        'users': UsersRepository,
        'configuration': ConfigurationRepository,
        'image_source': ImageSourceRepository,
        'camera_calibration': CameraCalibrationRepository,
        'image_generator': ImageGeneratorRepository,
    }
    
    _instances: Dict[str, Any] = {}
    _logger = logging.getLogger(__name__)
    
    @classmethod
    def create_repository(cls, repository_type: str, **kwargs) -> Any:
        """
        Create a repository instance.
        
        Args:
            repository_type: Type of repository to create
            **kwargs: Additional arguments for repository initialization
            
        Returns:
            Repository instance
            
        Raises:
            ValueError: If repository type is not supported
        """
        if repository_type not in cls.REPOSITORY_TYPES:
            available_types = ', '.join(cls.REPOSITORY_TYPES.keys())
            raise ValueError(
                f"Unsupported repository type: {repository_type}. "
                f"Available types: {available_types}"
            )
        
        repository_class = cls.REPOSITORY_TYPES[repository_type]
        
        try:
            repository = repository_class(**kwargs)
            cls._logger.debug(f"Created repository: {repository_type}")
            return repository
            
        except Exception as e:
            cls._logger.error(f"Failed to create repository {repository_type}: {e}")
            raise
    
    @classmethod
    def get_repository(cls, repository_type: str, singleton: bool = True, **kwargs) -> Any:
        """
        Get a repository instance (optionally singleton).
        
        Args:
            repository_type: Type of repository to get
            singleton: Whether to use singleton pattern
            **kwargs: Additional arguments for repository initialization
            
        Returns:
            Repository instance
        """
        if singleton:
            if repository_type not in cls._instances:
                cls._instances[repository_type] = cls.create_repository(repository_type, **kwargs)
            return cls._instances[repository_type]
        else:
            return cls.create_repository(repository_type, **kwargs)
    
    @classmethod
    def create_multiple_repositories(cls, repository_types: list, singleton: bool = True) -> Dict[str, Any]:
        """
        Create multiple repositories at once.
        
        Args:
            repository_types: List of repository types to create
            singleton: Whether to use singleton pattern
            
        Returns:
            Dictionary mapping repository types to instances
        """
        repositories = {}
        
        for repo_type in repository_types:
            try:
                repositories[repo_type] = cls.get_repository(repo_type, singleton=singleton)
            except Exception as e:
                cls._logger.error(f"Failed to create repository {repo_type}: {e}")
                # Continue creating other repositories even if one fails
                
        cls._logger.info(f"Created {len(repositories)} repositories")
        return repositories
    
    @classmethod
    def clear_instances(cls) -> None:
        """Clear all singleton repository instances."""
        count = len(cls._instances)
        cls._instances.clear()
        cls._logger.info(f"Cleared {count} repository instances")
    
    @classmethod
    def get_available_types(cls) -> list:
        """Get list of available repository types."""
        return list(cls.REPOSITORY_TYPES.keys())
    
    @classmethod
    def is_type_available(cls, repository_type: str) -> bool:
        """Check if a repository type is available."""
        return repository_type in cls.REPOSITORY_TYPES


class ServiceRepositoryMixin:
    """
    Mixin to add repository management capabilities to services.
    """
    
    def __init__(self):
        self._repositories: Dict[str, Any] = {}
        self._repository_factory = RepositoryFactory()
    
    def add_repository(self, name: str, repository_type: str, singleton: bool = True) -> Any:
        """
        Add a repository to the service.
        
        Args:
            name: Name to store repository under
            repository_type: Type of repository to create
            singleton: Whether to use singleton pattern
            
        Returns:
            Created repository instance
        """
        repository = self._repository_factory.get_repository(repository_type, singleton=singleton)
        self._repositories[name] = repository
        
        if hasattr(self, 'logger'):
            self.logger.debug(f"Added repository '{name}' of type '{repository_type}'")
        
        return repository
    
    def get_repository(self, name: str) -> Optional[Any]:
        """
        Get a repository by name.
        
        Args:
            name: Repository name
            
        Returns:
            Repository instance or None if not found
        """
        return self._repositories.get(name)
    
    def has_repository(self, name: str) -> bool:
        """
        Check if a repository exists.
        
        Args:
            name: Repository name
            
        Returns:
            True if repository exists
        """
        return name in self._repositories
    
    def remove_repository(self, name: str) -> Optional[Any]:
        """
        Remove a repository.
        
        Args:
            name: Repository name
            
        Returns:
            Removed repository instance or None if not found
        """
        repository = self._repositories.pop(name, None)
        
        if hasattr(self, 'logger'):
            if repository:
                self.logger.debug(f"Removed repository '{name}'")
            else:
                self.logger.warning(f"Repository '{name}' not found for removal")
        
        return repository
    
    def get_all_repositories(self) -> Dict[str, Any]:
        """
        Get all repositories.
        
        Returns:
            Dictionary of all repositories
        """
        return self._repositories.copy()
    
    def clear_repositories(self) -> None:
        """Clear all repositories."""
        count = len(self._repositories)
        self._repositories.clear()
        
        if hasattr(self, 'logger'):
            self.logger.info(f"Cleared {count} repositories")


# Convenience functions for common repository patterns
def create_standard_service_repositories(service_type: str) -> Dict[str, Any]:
    """
    Create standard repositories for common service types.
    
    Args:
        service_type: Type of service ('camera', 'cnc', 'robot', etc.)
        
    Returns:
        Dictionary of created repositories
    """
    repository_mappings = {
        'camera': ['camera', 'camera_settings'],
        'cnc': ['cnc', 'location'],
        'robot': ['robot'],
        'components': ['components'],
        'custom_components': ['custom_components'],
        'algorithms': ['algorithms', 'references'],
        'auth': ['users'],
        'configuration': ['configuration'],
        'image_source': ['image_source', 'camera_calibration'],
        'image_generator': ['image_generator'],
    }
    
    repo_types = repository_mappings.get(service_type, [])
    if not repo_types:
        raise ValueError(f"No standard repositories defined for service type: {service_type}")
    
    return RepositoryFactory.create_multiple_repositories(repo_types)


def get_repository_for_service(service_name: str, repository_type: str) -> Any:
    """
    Get a repository instance for a specific service.
    
    Args:
        service_name: Name of the service
        repository_type: Type of repository needed
        
    Returns:
        Repository instance
    """
    return RepositoryFactory.get_repository(repository_type, singleton=True)

