"""
Repository Factory

Centralizes repository creation and management to eliminate duplication.
Progressive migration to GenericRepository while maintaining backward compatibility.
"""

import logging
from typing import Dict, Type, Any, Optional
from repo.generic_repository import GenericRepository
# Keep old imports for backward compatibility during migration
from repo.repositories import (
    CameraRepository, CameraSettingsRepository,
    ComponentsRepository, CustomComponentsRepository,
    CncRepository, LocationRepository,
    RobotRepository, RobotPositionsRepository,
    AlgorithmsRepository, ReferencesRepository, UsersRepository,
    ConfigurationRepository, ImageSourceRepository,
    CameraCalibrationRepository, ImageGeneratorRepository,
    ProfilometerRepository, StereoCalibrationRepository
)
# Note: ComponentsRepository, ReferencesRepository, and ImageGeneratorRepository 
# have been consolidated but maintain the same interface


class RepositoryFactory:
    """
    Factory class for creating and managing repository instances.
    Progressively migrating to GenericRepository to eliminate duplication.
    """
    
    # Repository type mapping - maps to both old classes and db_names
    REPOSITORY_TYPES = {
        'camera': {'class': CameraRepository, 'db_name': 'cameras'},
        'camera_settings': {'class': CameraSettingsRepository, 'db_name': 'camera_settings'},
        'components': {'class': ComponentsRepository, 'db_name': 'components'},  # Consolidated
        'custom_components': {'class': CustomComponentsRepository, 'db_name': 'custom_components'},
        'cnc': {'class': CncRepository, 'db_name': 'cnc'},
        'location': {'class': LocationRepository, 'db_name': 'locations'},
        'robot': {'class': RobotRepository, 'db_name': 'robot'},
        'robot_positions': {'class': RobotPositionsRepository, 'db_name': 'robot_positions'},
        'algorithms': {'class': AlgorithmsRepository, 'db_name': 'algorithms'},
        'references': {'class': ReferencesRepository, 'db_name': 'references'},  # Consolidated
        'users': {'class': UsersRepository, 'db_name': 'users'},
        'configuration': {'class': ConfigurationRepository, 'db_name': 'configurations'},
        'image_source': {'class': ImageSourceRepository, 'db_name': 'image_source'},
        'camera_calibration': {'class': CameraCalibrationRepository, 'db_name': 'camera_calibration'},
        'image_generator': {'class': ImageGeneratorRepository, 'db_name': 'image_generators'},  # Consolidated
        'profilometer': {'class': ProfilometerRepository, 'db_name': 'profilometer'},
        'stereo_calibration': {'class': StereoCalibrationRepository, 'db_name': 'stereo_calibration'},
    }
    
    # List of repository types that have been migrated to GenericRepository
    # Start with least critical and gradually add more
    USE_GENERIC_FOR = [
        # Already migrated and tested
        'custom_components',     # Least critical - safe to migrate
        'camera_calibration',   # Isolated usage
        'location',             # CNC positioning data - safe to migrate
        'users',                # User management - test authentication carefully
        'robot_positions',      # Robot waypoints - safe to migrate
        
        # Safe to migrate - pure CRUD repositories (no custom methods)
        'cnc',                 # Simple CRUD - CNC settings
        'robot',               # Simple CRUD - robot settings
        'profilometer',        # Simple CRUD - profilometer settings
        'image_source',        # Simple CRUD - image source configurations
        'stereo_calibration',  # Simple CRUD - stereo calibration data
        
        # CONSOLIDATED (Phase 1 complete - now simple wrapper classes):
        # 'components' - Consolidated to simple BaseRepo wrapper
        # 'references' - Consolidated to simple BaseRepo wrapper  
        # 'image_generator' - Consolidated to simple BaseRepo wrapper
        
        # KEEP AS LEGACY (have custom methods - need special handling):
        # 'camera_settings' - has read_all_by_type method
        # 'camera' - has read_all_type method
        # 'algorithms' - has get_type_from_uid method
        # 'configuration' - has read_part_number method  
        # 'inspections' - has complex custom logic
    ]
    
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
        
        repo_config = cls.REPOSITORY_TYPES[repository_type]
        
        try:
            # Use GenericRepository for migrated types
            if repository_type in cls.USE_GENERIC_FOR:
                repository = GenericRepository(repo_config['db_name'], **kwargs)
                cls._logger.debug(f"Created GenericRepository for: {repository_type} (db: {repo_config['db_name']})")
            else:
                # Use old class for non-migrated types
                repository_class = repo_config['class']
                repository = repository_class(**kwargs)
                cls._logger.debug(f"Created legacy repository: {repository_type}")
            
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
    
    @classmethod
    def is_using_generic(cls, repository_type: str) -> bool:
        """Check if a repository type is using GenericRepository."""
        return repository_type in cls.USE_GENERIC_FOR
    
    @classmethod
    def migrate_to_generic(cls, repository_type: str) -> None:
        """
        Migrate a specific repository type to use GenericRepository.
        
        Args:
            repository_type: Type to migrate
        """
        if repository_type not in cls.REPOSITORY_TYPES:
            raise ValueError(f"Unknown repository type: {repository_type}")
            
        if repository_type not in cls.USE_GENERIC_FOR:
            cls.USE_GENERIC_FOR.append(repository_type)
            # Clear singleton instance to force recreation
            if repository_type in cls._instances:
                del cls._instances[repository_type]
            cls._logger.info(f"Migrated {repository_type} to use GenericRepository")
    
    @classmethod
    def rollback_from_generic(cls, repository_type: str) -> None:
        """
        Rollback a repository type to use legacy class.
        
        Args:
            repository_type: Type to rollback
        """
        if repository_type in cls.USE_GENERIC_FOR:
            cls.USE_GENERIC_FOR.remove(repository_type)
            # Clear singleton instance to force recreation
            if repository_type in cls._instances:
                del cls._instances[repository_type]
            cls._logger.info(f"Rolled back {repository_type} to use legacy repository")


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
            name: Name to use for the repository in this service
            repository_type: Type of repository to create
            singleton: Whether to use singleton pattern
            
        Returns:
            Repository instance
        """
        repository = self._repository_factory.get_repository(repository_type, singleton=singleton)
        self._repositories[name] = repository
        return repository
    
    def get_repository(self, name: str) -> Any:
        """
        Get a repository by name.
        
        Args:
            name: Repository name
            
        Returns:
            Repository instance or None
        """
        return self._repositories.get(name)
    
    def list_repositories(self) -> list:
        """List all repository names in this service."""
        return list(self._repositories.keys())


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