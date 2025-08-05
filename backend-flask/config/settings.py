"""
Main Settings Configuration

Centralized configuration management for the Industrial Vision Application.
Uses Pydantic for validation and environment variable support.
"""

import os
from functools import lru_cache
from typing import List, Optional, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from pathlib import Path

from .database import DatabaseConfig
from .server import ServerConfig
from .security import SecurityConfig
from .logging_config import LoggingConfig
from .hardware import HardwareConfig


class Settings(BaseSettings):
    """
    Main application settings class.
    
    This class consolidates all configuration settings and provides
    environment variable support with validation.
    """
    
    # Application Information
    app_name: str = Field(default="Industrial Vision System", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    app_description: str = Field(default="Advanced computer vision system for industrial inspection", description="Application description")
    
    # Environment
    environment: str = Field(default="development", description="Application environment (development/production)")
    debug: bool = Field(default=True, description="Enable debug mode")
    development_mode: bool = Field(default=True, description="Enable development mode features")
    
    # Project Paths
    project_root: str = Field(default_factory=lambda: str(Path(__file__).parent.parent.resolve()), description="Project root directory")
    data_directory: str = Field(default="", description="Data directory path")
    config_directory: str = Field(default="", description="Configuration directory path")
    reports_directory: str = Field(default="", description="Reports directory path")
    
    # Configuration Components
    database: DatabaseConfig = Field(default_factory=DatabaseConfig, description="Database configuration")
    server: ServerConfig = Field(default_factory=ServerConfig, description="Server configuration")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="Security configuration")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    hardware: HardwareConfig = Field(default_factory=HardwareConfig, description="Hardware configuration")
    
    # CNC Configuration
    cnc_poll_interval: float = Field(default=0.2, ge=0.01, le=1.0, description="CNC polling interval in seconds")
    cnc_timeout: int = Field(default=30, ge=1, le=300, description="CNC operation timeout in seconds")
    cnc_max_retries: int = Field(default=3, ge=1, le=10, description="Maximum CNC operation retries")
    
    # WebSocket Configuration
    websocket_batch_interval: float = Field(default=0.05, ge=0.01, le=1.0, description="WebSocket message batching interval")
    websocket_batch_size: int = Field(default=10, ge=1, le=100, description="Maximum messages per WebSocket batch")
    websocket_heartbeat_interval: int = Field(default=30, ge=5, le=300, description="WebSocket heartbeat interval in seconds")
    
    # Camera Configuration
    camera_timeout: int = Field(default=5, ge=1, le=60, description="Camera operation timeout in seconds")
    camera_retry_attempts: int = Field(default=3, ge=1, le=10, description="Camera connection retry attempts")
    
    # Robot Configuration
    robot_timeout: int = Field(default=30, ge=1, le=300, description="Robot operation timeout in seconds")
    robot_safety_limits: bool = Field(default=True, description="Enable robot safety limits")
    
    # Performance Configuration
    max_concurrent_operations: int = Field(default=10, ge=1, le=100, description="Maximum concurrent operations")
    operation_timeout: int = Field(default=300, ge=30, le=3600, description="General operation timeout in seconds")
    
    # Feature Flags
    enable_audio_feedback: bool = Field(default=True, description="Enable audio feedback")
    enable_advanced_logging: bool = Field(default=True, description="Enable advanced logging features")
    enable_performance_monitoring: bool = Field(default=False, description="Enable performance monitoring")
    enable_auto_backup: bool = Field(default=True, description="Enable automatic configuration backup")
    
    # External Services
    external_api_timeout: int = Field(default=30, ge=5, le=300, description="External API timeout in seconds")
    external_api_retries: int = Field(default=3, ge=1, le=10, description="External API retry attempts")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = "AOI_"  # Environment variables should be prefixed with AOI_
        
        # Allow extra fields for future extensibility
        extra = "allow"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_directories()
    
    def _setup_directories(self):
        """Setup and ensure required directories exist."""
        if not self.data_directory:
            self.data_directory = os.path.join(self.project_root, "data")
        
        if not self.config_directory:
            self.config_directory = os.path.join(self.project_root, "config_db")
        
        if not self.reports_directory:
            self.reports_directory = os.path.join(self.project_root, "reports")
        
        # Ensure directories exist
        for directory in [self.data_directory, self.config_directory, self.reports_directory]:
            os.makedirs(directory, exist_ok=True)
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment setting."""
        allowed_environments = ["development", "testing", "staging", "production"]
        if v.lower() not in allowed_environments:
            raise ValueError(f"Environment must be one of: {allowed_environments}")
        return v.lower()
    
    @field_validator("cnc_poll_interval")
    @classmethod
    def validate_cnc_poll_interval(cls, v):
        """Validate CNC polling interval."""
        if v < 0.01:
            raise ValueError("CNC poll interval must be at least 0.01 seconds")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development" or self.development_mode
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production" and not self.development_mode
    
    def get_database_url(self) -> str:
        """Get database connection URL."""
        return self.database.get_connection_url()
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment."""
        return self.server.get_cors_origins(self.is_development)
    
    def get_log_level(self) -> str:
        """Get appropriate log level."""
        return self.logging.get_log_level(self.is_development)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return self.dict()
    
    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update settings from dictionary."""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def save_to_file(self, file_path: str) -> None:
        """Save current settings to file."""
        import json
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
    
    def load_from_file(self, file_path: str) -> None:
        """Load settings from file."""
        import json
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                config_dict = json.load(f)
                self.update_from_dict(config_dict)


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings instance.
    
    This function is cached to ensure a single instance throughout the application.
    """
    return Settings()


# Convenience function for getting specific configuration sections
def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return get_settings().database


def get_server_config() -> ServerConfig:
    """Get server configuration."""
    return get_settings().server


def get_security_config() -> SecurityConfig:
    """Get security configuration."""
    return get_settings().security


def get_logging_config() -> LoggingConfig:
    """Get logging configuration."""
    return get_settings().logging


def get_hardware_config() -> HardwareConfig:
    """Get hardware configuration."""
    return get_settings().hardware

