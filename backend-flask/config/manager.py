"""
Configuration Manager

Provides centralized configuration management and integration with existing systems.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .settings import Settings, get_settings
from src.metaclasses.singleton import Singleton


class ConfigurationManager(metaclass=Singleton):
    """
    Configuration Manager for the Industrial Vision Application.
    
    This class provides a centralized way to manage all application configurations,
    integrating the new centralized system with existing configuration patterns.
    """
    
    def __init__(self):
        self._settings: Optional[Settings] = None
        self._logger = logging.getLogger(__name__)
        self._config_file_path = None
        self._environment_overrides = {}
        
    @property
    def settings(self) -> Settings:
        """Get the current settings instance."""
        if self._settings is None:
            self._settings = get_settings()
        return self._settings
    
    def initialize(self, config_file: Optional[str] = None, environment_overrides: Optional[Dict[str, Any]] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Optional path to configuration file
            environment_overrides: Optional environment-specific overrides
        """
        try:
            self._logger.info("Initializing Configuration Manager...")
            
            # Load from file if provided
            if config_file and os.path.exists(config_file):
                self._config_file_path = config_file
                self.load_from_file(config_file)
                self._logger.info(f"Loaded configuration from: {config_file}")
            
            # Apply environment overrides
            if environment_overrides:
                self._environment_overrides = environment_overrides
                self.apply_overrides(environment_overrides)
                self._logger.info("Applied environment overrides")
            
            # Validate configuration
            self._validate_configuration()
            
            # Setup directories
            self._setup_directories()
            
            self._logger.info("Configuration Manager initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize Configuration Manager: {e}")
            raise
    
    def load_from_file(self, file_path: str) -> None:
        """Load configuration from file."""
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            # Update settings with file data
            self.settings.update_from_dict(config_data)
            self._config_file_path = file_path
            
        except Exception as e:
            self._logger.error(f"Failed to load configuration from {file_path}: {e}")
            raise
    
    def save_to_file(self, file_path: Optional[str] = None) -> None:
        """Save current configuration to file."""
        try:
            target_path = file_path or self._config_file_path
            if not target_path:
                target_path = os.path.join(self.settings.config_directory, "application_config.json")
            
            self.settings.save_to_file(target_path)
            self._config_file_path = target_path
            self._logger.info(f"Configuration saved to: {target_path}")
            
        except Exception as e:
            self._logger.error(f"Failed to save configuration: {e}")
            raise
    
    def apply_overrides(self, overrides: Dict[str, Any]) -> None:
        """Apply configuration overrides."""
        try:
            self.settings.update_from_dict(overrides)
            self._environment_overrides.update(overrides)
            
        except Exception as e:
            self._logger.error(f"Failed to apply configuration overrides: {e}")
            raise
    
    def get_config_section(self, section: str) -> Any:
        """Get a specific configuration section."""
        try:
            return getattr(self.settings, section)
        except AttributeError:
            self._logger.warning(f"Configuration section '{section}' not found")
            return None
    
    def update_config_section(self, section: str, config: Dict[str, Any]) -> None:
        """Update a specific configuration section."""
        try:
            if hasattr(self.settings, section):
                current_config = getattr(self.settings, section)
                if hasattr(current_config, 'update_from_dict'):
                    current_config.update_from_dict(config)
                else:
                    # For simple values, update directly
                    setattr(self.settings, section, config)
                self._logger.info(f"Updated configuration section: {section}")
            else:
                self._logger.warning(f"Configuration section '{section}' not found")
                
        except Exception as e:
            self._logger.error(f"Failed to update configuration section '{section}': {e}")
            raise
    
    def get_legacy_config(self, component: str) -> Dict[str, Any]:
        """
        Get configuration in legacy format for backward compatibility.
        
        This method provides configuration data in the format expected by
        existing components that haven't been migrated to the new system yet.
        """
        try:
            if component == "cnc":
                return {
                    "poll_interval": self.settings.cnc_poll_interval,
                    "timeout": self.settings.cnc_timeout,
                    "max_retries": self.settings.cnc_max_retries,
                    "websocket_batch_interval": self.settings.websocket_batch_interval,
                    "websocket_batch_size": self.settings.websocket_batch_size,
                }
            
            elif component == "camera":
                return {
                    "timeout": self.settings.camera_timeout,
                    "retry_attempts": self.settings.camera_retry_attempts,
                }
            
            elif component == "robot":
                return {
                    "timeout": self.settings.robot_timeout,
                    "safety_limits": self.settings.robot_safety_limits,
                }
            
            elif component == "database":
                return {
                    "type": self.settings.database.db_type,
                    "path": self.settings.database.sqlite_path,
                    "timeout": self.settings.database.sqlite_timeout,
                }
            
            elif component == "server":
                return {
                    "host": self.settings.server.host,
                    "port": self.settings.server.port,
                    "cors_origins": self.settings.get_cors_origins(),
                    "development_mode": self.settings.is_development,
                }
            
            else:
                self._logger.warning(f"Unknown legacy component: {component}")
                return {}
                
        except Exception as e:
            self._logger.error(f"Failed to get legacy config for {component}: {e}")
            return {}
    
    def _validate_configuration(self) -> None:
        """Validate the current configuration."""
        try:
            # Basic validation - the Pydantic models handle most validation
            if not self.settings.project_root:
                raise ValueError("Project root not configured")
            
            if not os.path.exists(self.settings.project_root):
                raise ValueError(f"Project root does not exist: {self.settings.project_root}")
            
            # Validate critical paths
            for path_name, path_value in [
                ("data_directory", self.settings.data_directory),
                ("config_directory", self.settings.config_directory),
            ]:
                if not path_value:
                    raise ValueError(f"{path_name} not configured")
            
            self._logger.info("Configuration validation passed")
            
        except Exception as e:
            self._logger.error(f"Configuration validation failed: {e}")
            raise
    
    def _setup_directories(self) -> None:
        """Setup required directories."""
        try:
            directories = [
                self.settings.data_directory,
                self.settings.config_directory,
                self.settings.reports_directory,
                self.settings.logging.log_directory,
            ]
            
            for directory in directories:
                if directory:
                    os.makedirs(directory, exist_ok=True)
                    self._logger.debug(f"Ensured directory exists: {directory}")
            
        except Exception as e:
            self._logger.error(f"Failed to setup directories: {e}")
            raise
    
    def reload_configuration(self) -> None:
        """Reload configuration from file."""
        try:
            if self._config_file_path and os.path.exists(self._config_file_path):
                self.load_from_file(self._config_file_path)
                
                # Reapply environment overrides
                if self._environment_overrides:
                    self.apply_overrides(self._environment_overrides)
                
                self._logger.info("Configuration reloaded successfully")
            else:
                self._logger.warning("No configuration file to reload from")
                
        except Exception as e:
            self._logger.error(f"Failed to reload configuration: {e}")
            raise
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information."""
        return {
            "environment": self.settings.environment,
            "debug": self.settings.debug,
            "development_mode": self.settings.development_mode,
            "is_production": self.settings.is_production,
            "project_root": self.settings.project_root,
            "config_file": self._config_file_path,
        }
    
    def export_configuration(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Export current configuration."""
        try:
            config_dict = self.settings.to_dict()
            
            if not include_sensitive:
                # Remove sensitive information
                sensitive_keys = [
                    "jwt_secret_key",
                    "csrf_secret_key", 
                    "encryption_key",
                    "api_keys",
                    "postgres_password",
                    "mysql_password",
                ]
                
                def remove_sensitive(obj, keys):
                    if isinstance(obj, dict):
                        for key in list(obj.keys()):
                            if any(sensitive in key.lower() for sensitive in ["password", "secret", "key", "token"]):
                                obj[key] = "***REDACTED***"
                            elif isinstance(obj[key], dict):
                                remove_sensitive(obj[key], keys)
                
                remove_sensitive(config_dict, sensitive_keys)
            
            return config_dict
            
        except Exception as e:
            self._logger.error(f"Failed to export configuration: {e}")
            raise
    
    def create_backup(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the current configuration."""
        try:
            if not backup_path:
                timestamp = Path().cwd().name
                backup_filename = f"config_backup_{timestamp}.json"
                backup_path = os.path.join(self.settings.config_directory, "backups", backup_filename)
            
            # Ensure backup directory exists
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Save configuration to backup
            self.save_to_file(backup_path)
            
            self._logger.info(f"Configuration backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            self._logger.error(f"Failed to create configuration backup: {e}")
            raise


# Global configuration manager instance
config_manager = ConfigurationManager()


def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    return config_manager


def get_legacy_config(component: str) -> Dict[str, Any]:
    """Convenience function to get legacy configuration format."""
    return config_manager.get_legacy_config(component)

