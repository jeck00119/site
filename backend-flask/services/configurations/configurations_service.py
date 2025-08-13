import os
import pathlib
import shutil
import time
import logging
from typing import Dict, Any

from repo.repositories import ConfigurationRepository, IdentificationsRepository, AudioEventsRepository, InspectionsRepository
from services.base.repository_factory import RepositoryFactory
from services.camera.camera_service import CameraService
from services.cnc.cnc_service import CncService
from services.components.components_service import ComponentsService
from services.configurations.configuration_model import ConfigurationModel
from services.configurations.configuration_cache import ConfigurationCache
from services.image_source.image_source_service import ImageSourceService
from services.robot.robot_service import RobotService
from src.metaclasses.singleton import Singleton

directory_path = str(pathlib.Path(__file__).parent.parent.parent.resolve())


class ConfigurationService(metaclass=Singleton):
    def __init__(self):
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Core repositories
        self.configuration_repository = ConfigurationRepository()
        
        # Configuration cache for performance
        self.config_cache = ConfigurationCache()
        
        # Track last camera settings to avoid unnecessary reinit
        self._last_camera_settings = None
        
        # Data repositories - Use RepositoryFactory for centralized management
        # This eliminates 17+ manual repository instantiations and redundant code
        repository_types = [
            'algorithms', 'camera', 'camera_settings', 'cnc', 'components', 
            'custom_components', 'image_generator', 'image_source', 'location', 
            'profilometer', 'references', 'robot', 'camera_calibration', 
            'stereo_calibration', 'robot_positions'
        ]
        
        # Create repositories using factory pattern
        repositories = RepositoryFactory.create_multiple_repositories(repository_types, singleton=True)
        
        # Assign repositories to maintain backward compatibility
        self.algorithms_repository = repositories['algorithms']
        self.camera_repository = repositories['camera']
        self.camera_settings_repository = repositories['camera_settings']
        self.cnc_repository = repositories['cnc']
        self.components_repository = repositories['components']
        self.custom_components_repository = repositories['custom_components']
        self.image_generator_repository = repositories['image_generator']
        self.image_source_repository = repositories['image_source']
        self.locations_repository = repositories['location']
        self.profilometer_repository = repositories['profilometer']
        self.references_repository = repositories['references']
        self.robot_repository = repositories['robot']
        self.camera_calibration_repository = repositories['camera_calibration']
        self.stereo_calibration_repository = repositories['stereo_calibration']
        self.robot_positions_repository = repositories['robot_positions']
        
        # Legacy repositories that still need manual instantiation (have custom methods)
        self.identifications_repository = IdentificationsRepository()
        self.audio_repository = AudioEventsRepository()
        self.inspections_repository = InspectionsRepository()
        
        self.logger.info(f"Initialized repositories: {len(repositories)} via factory, 3 legacy")

        # Repository mapping for atomic operations
        self.repository_mapping = {
            'algorithms.json': self.algorithms_repository,
            'cameras.json': self.camera_repository,
            'camera_settings.json': self.camera_settings_repository,
            'cnc.json': self.cnc_repository,
            'components.json': self.components_repository,
            'identifications.json': self.identifications_repository,
            'custom_components.json': self.custom_components_repository,
            'image_generator.json': self.image_generator_repository,
            'image_source.json': self.image_source_repository,
            'inspections.json': self.inspections_repository,
            'locations.json': self.locations_repository,
            'profilometer.json': self.profilometer_repository,
            'references.json': self.references_repository,
            'robot.json': self.robot_repository,
            'audio_events.json': self.audio_repository,
            'camera_calibration.json': self.camera_calibration_repository,
            'stereo_calibration.json': self.stereo_calibration_repository,
            'robot_positions.json': self.robot_positions_repository
        }

        # Services
        self.image_source_service = ImageSourceService()
        self.camera_service = CameraService()
        self.components_service = ComponentsService()
        self.cnc_service = CncService()
        self.robot_service = RobotService()

        # Current state
        self.current_configuration_uid = None
        self.current_configuration_name = None

        # Change notification flags
        self.configuration_changed_socket = False
        self.configuration_changed_process = False
        
        # Initialize cache with common configurations
        try:
            self.config_cache.warm_cache_with_common_configs()
        except Exception as e:
            self.logger.warning(f"Failed to warm cache: {e}")

    def get_current_configuration_uid(self):
        return self.current_configuration_uid

    @staticmethod
    def post_configuration(configuration_model: ConfigurationModel):
        config_name = configuration_model.name
        path = directory_path + "/config_db/" + config_name
        
        # Use makedirs with exist_ok=True for safety and consistency
        os.makedirs(path, exist_ok=True)
        logging.getLogger(__name__).info(f"Created configuration directory: {path}")

    def copy_configuration(self, configuration_model: ConfigurationModel, original_configuration_uid: str):
        original_config = self.configuration_repository.read_id(original_configuration_uid)
        
        original_path = directory_path + "/config_db/" + original_config['name']
        new_path = directory_path + "/config_db/" + configuration_model.name
        
        if not os.path.exists(original_path):
            raise FileNotFoundError(f"Source configuration directory not found: {original_path}")
        
        # Don't call post_configuration here since it creates an empty directory
        # Just copy the entire configuration directly
        if os.path.exists(new_path):
            # If directory exists but is empty (from a failed attempt), remove it
            if not os.listdir(new_path):
                os.rmdir(new_path)
                self.logger.info(f"Removed empty directory: {new_path}")
            else:
                raise FileExistsError(f"Target configuration directory already exists and is not empty: {new_path}")
        
        shutil.copytree(original_path, new_path)
        self.logger.info(f"Copied configuration: {original_path} -> {new_path}")

    @staticmethod
    def delete_configuration(configuration_model: ConfigurationModel):
        name = configuration_model.name
        path = directory_path + "/config_db/" + name
        
        if not os.path.exists(path):
            logging.getLogger(__name__).warning(f"Configuration directory not found for deletion: {path}")
            return
            
        shutil.rmtree(path)
        logging.getLogger(__name__).info(f"Deleted configuration directory: {path}")

    @staticmethod
    def update_configuration(old_configuration: ConfigurationModel, configuration_model: ConfigurationModel):
        old_name = old_configuration.name
        old_path = directory_path + "/config_db/" + old_name
        new_name = configuration_model.name
        new_path = directory_path + "/config_db/" + new_name
        
        # Windows-safe directory rename using copy + delete approach
        if not os.path.exists(old_path):
            raise FileNotFoundError(f"Configuration directory not found: {old_path}")
        
        if os.path.exists(new_path):
            raise FileExistsError(f"Target configuration directory already exists: {new_path}")
        
        try:
            # Copy directory to new location
            shutil.copytree(old_path, new_path)
            logging.getLogger(__name__).info(f"Copied configuration directory: {old_path} -> {new_path}")
            
            # Remove old directory after successful copy
            shutil.rmtree(old_path)
            logging.getLogger(__name__).info(f"Removed old configuration directory: {old_path}")
            
        except Exception as e:
            # Cleanup partial copy on failure
            if os.path.exists(new_path):
                try:
                    shutil.rmtree(new_path)
                except:
                    pass
            raise RuntimeError(f"Failed to update configuration directory: {e}")

    def load_configuration(self, configuration_uid):
        """Load configuration by UID using optimized atomic switching."""
        start_time = time.time()
        
        configuration = self.configuration_repository.read_id(configuration_uid)
        configuration_model = ConfigurationModel(**configuration)
        
        self.logger.info(f"Loading configuration '{configuration_model.name}' (UID: {configuration_uid})")

        # Use atomic repository switching for better performance
        switch_start = time.time()
        self.set_repositories_atomic(configuration_model.name)
        self.logger.debug(f"Repository switch took {time.time() - switch_start:.3f}s")
        
        # Validate clean state
        validate_start = time.time()
        if not self.validate_clean_state(configuration_model.name):
            raise Exception(f"Clean state validation failed for configuration '{configuration_model.name}'")
        self.logger.debug(f"Validation took {time.time() - validate_start:.3f}s")

        # Reinitialize services
        reinit_start = time.time()
        self.reinit_services()
        self.logger.debug(f"Service reinitialization took {time.time() - reinit_start:.3f}s")
        
        self.set_configuration_flag()

        self.current_configuration_uid = configuration_uid
        
        total_time = time.time() - start_time
        self.logger.info(f"Configuration loaded successfully in {total_time:.3f}s")

    def load_configuration_part_number(self, part_number):
        """Load configuration by part number using optimized atomic switching."""
        try:
            start_time = time.time()
            
            configuration = self.configuration_repository.read_part_number(part_number)
            configuration_model = ConfigurationModel(**configuration)
            self.logger.info(f"Found configuration '{configuration_model.name}' for part number '{part_number}'")

            if self.current_configuration_uid != configuration_model.uid:
                self.logger.info(f"Switching from current config to '{configuration_model.name}'")
                
                # Use atomic switching for better performance
                self.set_repositories_atomic(configuration_model.name)
                
                # Validate clean state
                if not self.validate_clean_state(configuration_model.name):
                    raise Exception(f"Clean state validation failed for configuration '{configuration_model.name}'")

                self.reinit_services()
                self.current_configuration_uid = configuration_model.uid
                self.set_configuration_flag()
                
                total_time = time.time() - start_time
                self.logger.info(f"Part number configuration switch completed in {total_time:.3f}s")
            else:
                self.logger.info(f"Configuration '{configuration_model.name}' already loaded, skipping switch")

            return configuration_model
        except Exception as e:
            self.logger.info(f"ERROR: Exception when loading config for part '{part_number}': {e}")
            return None

    def reset_configuration_flag_socket(self):
        self.configuration_changed_socket = False

    def reset_configuration_flag_process(self):
        self.configuration_changed_process = False

    def set_configuration_flag(self):
        self.configuration_changed_socket = True
        self.configuration_changed_process = True

    def get_configuration_flag_socket(self):
        return self.configuration_changed_socket

    def get_configuration_flag_process(self):
        return self.configuration_changed_process

    def set_repositories(self, name):
        self.algorithms_repository.set_db(name)
        self.camera_repository.set_db(name)
        self.camera_settings_repository.set_db(name)
        self.cnc_repository.set_db(name)
        self.components_repository.set_db(name)
        self.identifications_repository.set_db(name)
        self.custom_components_repository.set_db(name)
        self.image_generator_repository.set_db(name)
        self.image_source_repository.set_db(name)
        self.inspections_repository.set_db(name)
        self.locations_repository.set_db(name)
        self.profilometer_repository.set_db(name)
        self.references_repository.set_db(name)
        self.robot_repository.set_db(name)
        self.audio_repository.set_db(name)
        self.camera_calibration_repository.set_db(name)
        self.stereo_calibration_repository.set_db(name)
        self.robot_positions_repository.set_db(name)
        
        # FIXED: Users should remain global, not configuration-specific
        # Removing user repository switching to prevent authentication issues
        # Users database should always point to the main config_db directory
        # from api.dependencies.services import get_service_by_type
        # from services.authentication.auth_service import AuthService
        # auth_service = get_service_by_type(AuthService)()
        # auth_service.users_repository.set_db(name)  # REMOVED - causes users to disappear
        self.logger.info(f"LEGACY: Configuration switched to: {name} (users remain global)")
        
    def clear_all_repositories(self) -> None:
        """
        Clear all repository state to ensure clean isolation.
        This prevents any leftover data from previous configurations.
        """
        start_time = time.time()
        self.logger.info("Clearing all repository state...")
        
        for repo in self.repository_mapping.values():
            repo.reset_db()
            
        clear_time = time.time() - start_time
        self.logger.info(f"All repositories cleared in {clear_time:.3f}s")
    
    def set_repositories_atomic(self, config_name: str) -> None:
        """
        Atomic repository switching using cached configuration data.
        
        This method provides the same clean state isolation as set_repositories()
        but with dramatically better performance through caching.
        
        Args:
            config_name: Name of configuration to switch to
        """
        start_time = time.time()
        self.logger.info(f"ATOMIC: Switching to configuration '{config_name}'")
        
        # Store previous state for rollback
        previous_config_name = self.current_configuration_name
        
        try:
            # 1. Get cached configuration data (fast) - this validates config exists
            config_data = self.config_cache.get_configuration(config_name)
            
            # 2. Clear all repositories (ensures clean state)
            self.clear_all_repositories()
            
            # 3. Set all repositories in one atomic operation
            for repo in self.repository_mapping.values():
                repo.set_db(config_name)
            
            # 4. Update current state
            self.current_configuration_name = config_name
            
            switch_time = time.time() - start_time
            self.logger.info(f"ATOMIC: Configuration switch completed in {switch_time:.3f}s")
            
        except Exception as e:
            # On failure, restore previous state or clear everything
            self.logger.info(f"ERROR: Atomic switch failed: {e}")
            
            if previous_config_name:
                try:
                    self.logger.info(f"Attempting to restore previous configuration '{previous_config_name}'")
                    # Try to restore previous configuration
                    for repo in self.repository_mapping.values():
                        repo.set_db(previous_config_name)
                    self.current_configuration_name = previous_config_name
                    self.logger.info(f"Successfully restored previous configuration '{previous_config_name}'")
                except Exception as restore_error:
                    self.logger.info(f"Failed to restore previous config: {restore_error}")
                    self.clear_all_repositories()
                    self.current_configuration_name = None
            else:
                # No previous state, just clear everything
                self.clear_all_repositories()
                self.current_configuration_name = None
            
            raise
    
    def validate_clean_state(self, expected_config: str) -> bool:
        """
        Validate that all repositories are correctly set to the expected configuration
        and that no leftover data exists from previous configurations.
        
        Args:
            expected_config: Configuration name that should be loaded
            
        Returns:
            True if state is clean, False if contamination detected
        """
        self.logger.info(f"Validating clean state for '{expected_config}'")
        
        validation_issues = []
        
        # Check each repository points to correct configuration
        for file_name, repo in self.repository_mapping.items():
            if hasattr(repo, 'get_configuration_path'):
                repo_path = repo.get_configuration_path()
                
                # Handle different possible base paths (E:\site vs E:\site\backend-flask)
                expected_path_1 = f"{directory_path}/config_db/{expected_config}"
                expected_path_2 = f"{os.getcwd()}/config_db/{expected_config}"
                
                # Normalize paths for comparison (convert backslashes to forward slashes)
                repo_path_norm = repo_path.replace('\\', '/')
                expected_path_1_norm = expected_path_1.replace('\\', '/')
                expected_path_2_norm = expected_path_2.replace('\\', '/')
                
                if repo_path_norm != expected_path_1_norm and repo_path_norm != expected_path_2_norm:
                    validation_issues.append(f"{file_name}: path mismatch (expected: {expected_path_1_norm} or {expected_path_2_norm}, got: {repo_path_norm})")
        
        # Check current state matches
        if self.current_configuration_name != expected_config:
            validation_issues.append(f"Current config mismatch: expected {expected_config}, got {self.current_configuration_name}")
        
        if validation_issues:
            self.logger.error(f"VALIDATION FAILED: {len(validation_issues)} issues found:")
            for issue in validation_issues:
                self.logger.error(f"  - {issue}")
            return False
        
        self.logger.info(f"Clean state validation PASSED for '{expected_config}'")
        return True

    def reset_dbs(self):
        self.algorithms_repository.reset_db()
        self.camera_repository.reset_db()
        self.camera_settings_repository.reset_db()
        self.cnc_repository.reset_db()
        self.components_repository.reset_db()
        self.identifications_repository.reset_db()
        self.custom_components_repository.reset_db()
        self.image_generator_repository.reset_db()
        self.image_source_repository.reset_db()
        self.inspections_repository.reset_db()
        self.locations_repository.reset_db()
        self.profilometer_repository.reset_db()
        self.references_repository.reset_db()
        self.robot_repository.reset_db()
        self.audio_repository.reset_db()
        self.camera_calibration_repository.reset_db()
        self.stereo_calibration_repository.reset_db()
        self.robot_positions_repository.reset_db()

        self.current_configuration_uid = None

    def reinit_services(self):
        # Only reinitialize services that actually need configuration changes
        img_start = time.time()
        self.image_source_service.initialize_all_image_sources()
        self.logger.debug(f"Image source init took {time.time() - img_start:.3f}s")
        
        # Camera initialization is slow (4+ seconds) - only do it if camera config actually changed
        cam_start = time.time()
        try:
            current_camera_settings = self.camera_settings_repository.read_all()
            
            # Check if camera settings actually changed
            camera_settings_changed = (current_camera_settings != self._last_camera_settings)
            
            if camera_settings_changed:
                self.logger.info("Camera settings changed, reinitializing cameras...")
                cam_init_start = time.time()
                self.camera_service.initialize_all_cameras()
                self.logger.debug(f"Camera init took {time.time() - cam_init_start:.3f}s")
                self._last_camera_settings = current_camera_settings
            else:
                self.logger.info("Camera settings unchanged, skipping camera reinitialization")
        except Exception as e:
            # If no camera settings or error, skip camera initialization
            self.logger.info(f"Skipping camera initialization: {e}")
            pass
        self.logger.debug(f"Total camera check/init took {time.time() - cam_start:.3f}s")
            
        comp_start = time.time()
        self.components_service.start_service()
        self.logger.debug(f"Components service took {time.time() - comp_start:.3f}s")
        
        cnc_start = time.time()
        self.cnc_service.start_cnc_service()
        self.logger.debug(f"CNC service took {time.time() - cnc_start:.3f}s")
        
        robot_start = time.time()
        self.robot_service.start_robot_service()
        self.logger.debug(f"Robot service took {time.time() - robot_start:.3f}s")

    def get_current_configuration_name(self):
        if self.current_configuration_uid:
            configuration = self.configuration_repository.read_id(self.current_configuration_uid)
            return configuration["name"]

        return None

    def get_current_configuration_part_number(self):
        if self.current_configuration_uid:
            configuration = self.configuration_repository.read_id(self.current_configuration_uid)
            return configuration["part_number"]

        return None
