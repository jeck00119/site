"""
Generic Repository Implementation

Eliminates the need for 21+ duplicate repository classes.
Each repository only differs by db_name, so we can use a single generic class.
"""

from typing import Optional, Type, Any, Dict, List
from repo.abstract_repo import BaseRepo
from repo.repository_exceptions import UidNotFound, NoConfigurationChosen


class GenericRepository(BaseRepo):
    """
    Generic repository that can be used for any entity type.
    Replaces 21+ duplicate repository classes.
    """
    
    def __init__(self, db_name: str, model_class: Optional[Type] = None):
        """
        Initialize generic repository.
        
        Args:
            db_name: Name of the database/collection
            model_class: Optional model class for type conversion
        """
        super().__init__(db_name=db_name)
        self.model_class = model_class
        self._db_name = db_name
    
    def convert_dict_to_model(self, data: dict) -> Any:
        """
        Convert dictionary to model instance if model_class is provided.
        
        Args:
            data: Dictionary data
            
        Returns:
            Model instance or original dict if no model_class
        """
        if self.model_class:
            return self.model_class(**data)
        return data
    
    def set_model_class(self, model_class: Type) -> None:
        """
        Set or update the model class for this repository.
        
        Args:
            model_class: Model class to use for conversions
        """
        self.model_class = model_class
    
    def __repr__(self) -> str:
        """String representation of the repository."""
        return f"GenericRepository(db_name='{self._db_name}')"


class RepositoryRegistry:
    """
    Registry for managing repository instances.
    Provides backward compatibility for existing code.
    """
    
    _instances: Dict[str, GenericRepository] = {}
    
    @classmethod
    def get_repository(cls, db_name: str, model_class: Optional[Type] = None) -> GenericRepository:
        """
        Get or create a repository instance.
        
        Args:
            db_name: Name of the database/collection
            model_class: Optional model class
            
        Returns:
            Repository instance
        """
        if db_name not in cls._instances:
            cls._instances[db_name] = GenericRepository(db_name, model_class)
        elif model_class and not cls._instances[db_name].model_class:
            # Update model class if provided and not already set
            cls._instances[db_name].set_model_class(model_class)
        
        return cls._instances[db_name]
    
    @classmethod
    def clear_instances(cls) -> None:
        """Clear all repository instances."""
        cls._instances.clear()


# Backward compatibility - create factory functions for each repository type
def create_image_source_repository():
    """Factory for ImageSourceRepository compatibility."""
    from services.image_source.image_source_model import ImageSourceModel
    return RepositoryRegistry.get_repository('image_source', ImageSourceModel)

def create_components_repository():
    """Factory for ComponentsRepository compatibility."""
    try:
        from services.components.components_model import ComponentModel
        model_class = ComponentModel
    except ImportError:
        model_class = None
    return RepositoryRegistry.get_repository('components', model_class)

def create_references_repository():
    """Factory for ReferencesRepository compatibility."""
    from services.references.references_model import ReferenceModel
    return RepositoryRegistry.get_repository('references', ReferenceModel)

def create_custom_components_repository():
    """Factory for CustomComponentsRepository compatibility."""
    from services.custom_components.custom_components_model import CustomComponentModel
    return RepositoryRegistry.get_repository('custom_components', CustomComponentModel)

def create_algorithms_repository():
    """Factory for AlgorithmsRepository compatibility."""
    return RepositoryRegistry.get_repository('algorithms')

def create_camera_repository():
    """Factory for CameraRepository compatibility."""
    from services.camera.camera_model import CameraModel
    return RepositoryRegistry.get_repository('camera', CameraModel)

def create_cnc_repository():
    """Factory for CncRepository compatibility."""
    return RepositoryRegistry.get_repository('cnc')

def create_robot_repository():
    """Factory for RobotRepository compatibility."""
    return RepositoryRegistry.get_repository('robot')

def create_users_repository():
    """Factory for UsersRepository compatibility."""
    return RepositoryRegistry.get_repository('users')

def create_configuration_repository():
    """Factory for ConfigurationRepository compatibility."""
    repo = RepositoryRegistry.get_repository('configurations')
    # Add the custom method for ConfigurationRepository
    def read_part_number(self, part_number):
        if self.db:
            found = self.find_by_query(lambda x: x.get("part_number") == part_number)
            if found:
                return found[0]
            else:
                raise UidNotFound
        else:
            raise NoConfigurationChosen
    
    # Bind the method to the instance
    import types
    repo.read_part_number = types.MethodType(read_part_number, repo)
    return repo

def create_camera_settings_repository():
    """Factory for CameraSettingsRepository compatibility."""
    return RepositoryRegistry.get_repository('camera_settings')

def create_camera_calibration_repository():
    """Factory for CameraCalibrationRepository compatibility."""
    return RepositoryRegistry.get_repository('camera_calibration')

def create_location_repository():
    """Factory for LocationRepository compatibility."""
    return RepositoryRegistry.get_repository('locations')

def create_identifications_repository():
    """Factory for IdentificationsRepository compatibility."""
    return RepositoryRegistry.get_repository('identifications')

def create_itac_repository():
    """Factory for ItacRepository compatibility."""
    repo = RepositoryRegistry.get_repository('itac')
    repo.set_db(configuration_name=None)
    return repo

def create_image_generator_repository():
    """Factory for ImageGeneratorRepository compatibility."""
    return RepositoryRegistry.get_repository('image_generators')

def create_robot_positions_repository():
    """Factory for RobotPositionsRepository compatibility."""
    return RepositoryRegistry.get_repository('robot_positions')

def create_profilometer_repository():
    """Factory for ProfilometerRepository compatibility."""
    return RepositoryRegistry.get_repository('profilometer')

def create_stereo_calibration_repository():
    """Factory for StereoCalibrationRepository compatibility."""
    return RepositoryRegistry.get_repository('stereo_calibration')

def create_inspections_repository():
    """Factory for InspectionsRepository compatibility."""
    return RepositoryRegistry.get_repository('inspections')

def create_media_events_repository():
    """Factory for MediaEventsRepository compatibility."""
    return RepositoryRegistry.get_repository('media_events')


# Repository type mapping for RepositoryFactory integration
REPOSITORY_TYPE_MAPPING = {
    'image_source': create_image_source_repository,
    'components': create_components_repository,
    'references': create_references_repository,
    'custom_components': create_custom_components_repository,
    'algorithms': create_algorithms_repository,
    'camera': create_camera_repository,
    'camera_settings': create_camera_settings_repository,
    'camera_calibration': create_camera_calibration_repository,
    'cnc': create_cnc_repository,
    'robot': create_robot_repository,
    'robot_positions': create_robot_positions_repository,
    'users': create_users_repository,
    'configuration': create_configuration_repository,
    'location': create_location_repository,
    'identifications': create_identifications_repository,
    'itac': create_itac_repository,
    'image_generator': create_image_generator_repository,
    'profilometer': create_profilometer_repository,
    'stereo_calibration': create_stereo_calibration_repository,
    'inspections': create_inspections_repository,
    'media_events': create_media_events_repository,
}