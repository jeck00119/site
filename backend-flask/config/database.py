"""
Database Configuration

Centralized database configuration for the Industrial Vision Application.
Uses JSON/TinyDB for unified data storage.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, validator


class DatabaseConfig(BaseModel):
    """Database configuration settings for JSON/TinyDB storage."""
    
    # Database Type - Fixed to JSON for unified storage
    db_type: str = Field(default="json", description="Database type (json only - unified TinyDB storage)")
    
    # JSON/TinyDB Configuration
    json_path: str = Field(default="config_db", description="JSON database directory path")
    json_indent: int = Field(default=4, ge=2, le=8, description="JSON file indentation")
    json_sort_keys: bool = Field(default=True, description="Sort keys in JSON files")
    
    # Performance Settings
    enable_query_logging: bool = Field(default=False, description="Enable database query logging")
    cache_size: int = Field(default=100, ge=10, le=1000, description="Database cache size")
    
    # Backup Settings
    enable_auto_backup: bool = Field(default=True, description="Enable automatic database backup")
    backup_interval_hours: int = Field(default=24, ge=1, le=168, description="Backup interval in hours")
    backup_retention_days: int = Field(default=7, ge=1, le=30, description="Backup retention period in days")
    backup_directory: str = Field(default="backups", description="Backup directory path")
    
    # Configuration Management
    config_directory: str = Field(default="config_db", description="Configuration database directory")
    default_configuration: Optional[str] = Field(default=None, description="Default configuration name")
    
    # File System Settings
    create_directories: bool = Field(default=True, description="Automatically create missing directories")
    file_mode: int = Field(default=0o644, description="File permissions for database files")
    
    class Config:
        env_prefix = "DB_"
        case_sensitive = False
    
    @validator("db_type")
    def validate_db_type(cls, v):
        """Validate that only JSON database type is supported."""
        if v != "json":
            raise ValueError("Only 'json' database type is supported for unified storage")
        return v
    
    @validator("json_path", "backup_directory", "config_directory")
    def validate_paths(cls, v):
        """Validate directory paths."""
        if not v or not isinstance(v, str):
            raise ValueError("Path must be a non-empty string")
        return v.strip()
    
    def get_database_path(self, configuration_name: Optional[str] = None) -> str:
        """Get the database path for a specific configuration."""
        base_path = os.path.abspath(self.json_path)
        
        if configuration_name:
            return os.path.join(base_path, configuration_name)
        else:
            return base_path
    
    def get_backup_path(self) -> str:
        """Get the backup directory path."""
        return os.path.abspath(self.backup_directory)
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        if self.create_directories:
            paths_to_create = [
                self.json_path,
                self.backup_directory,
                self.config_directory
            ]
            
            for path in paths_to_create:
                abs_path = os.path.abspath(path)
                os.makedirs(abs_path, mode=self.file_mode, exist_ok=True)
    
    def is_json_database(self) -> bool:
        """Check if using JSON database (always True in unified system)."""
        return True
    
    def get_connection_info(self) -> dict:
        """Get database connection information."""
        return {
            "type": self.db_type,
            "path": self.json_path,
            "config_directory": self.config_directory,
            "backup_directory": self.backup_directory,
            "settings": {
                "indent": self.json_indent,
                "sort_keys": self.json_sort_keys,
                "cache_size": self.cache_size
            }
        }