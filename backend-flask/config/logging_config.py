"""
Logging Configuration

Centralized logging configuration for the Industrial Vision Application.
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class LoggingConfig(BaseModel):
    """Logging configuration settings."""
    
    # Basic Logging Settings
    log_level: str = Field(default="INFO", description="Default log level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S", description="Date format for logs")
    
    # File Logging
    enable_file_logging: bool = Field(default=True, description="Enable logging to files")
    log_directory: str = Field(default="logs", description="Log files directory")
    log_filename: str = Field(default="application.log", description="Main log file name")
    max_log_size_mb: int = Field(default=10, ge=1, le=1000, description="Maximum log file size in MB")
    backup_count: int = Field(default=5, ge=1, le=100, description="Number of backup log files to keep")
    
    # Console Logging
    enable_console_logging: bool = Field(default=True, description="Enable logging to console")
    console_log_level: str = Field(default="INFO", description="Console log level")
    colored_console: bool = Field(default=True, description="Enable colored console output")
    
    # Structured Logging
    enable_json_logging: bool = Field(default=False, description="Enable JSON structured logging")
    json_log_filename: str = Field(default="application.json", description="JSON log file name")
    
    # Component-Specific Logging
    component_log_levels: Dict[str, str] = Field(
        default={
            "cnc": "INFO",
            "camera": "INFO", 
            "robot": "INFO",
            "database": "WARNING",
            "websocket": "INFO",
            "api": "INFO",
            "security": "WARNING"
        },
        description="Log levels for specific components"
    )
    
    # Performance Logging
    enable_performance_logging: bool = Field(default=False, description="Enable performance logging")
    performance_log_filename: str = Field(default="performance.log", description="Performance log file name")
    slow_operation_threshold_ms: int = Field(default=1000, ge=100, le=60000, description="Slow operation threshold in milliseconds")
    
    # Error Logging
    enable_error_logging: bool = Field(default=True, description="Enable dedicated error logging")
    error_log_filename: str = Field(default="errors.log", description="Error log file name")
    error_log_level: str = Field(default="ERROR", description="Error log level")
    
    # Audit Logging
    enable_audit_logging: bool = Field(default=True, description="Enable audit logging")
    audit_log_filename: str = Field(default="audit.log", description="Audit log file name")
    audit_events: List[str] = Field(
        default=["login", "logout", "config_change", "user_creation", "permission_change"],
        description="Events to audit"
    )
    
    # Security Logging
    enable_security_logging: bool = Field(default=True, description="Enable security logging")
    security_log_filename: str = Field(default="security.log", description="Security log file name")
    log_failed_logins: bool = Field(default=True, description="Log failed login attempts")
    log_suspicious_activity: bool = Field(default=True, description="Log suspicious activity")
    
    # Database Logging
    enable_database_logging: bool = Field(default=False, description="Enable database query logging")
    database_log_filename: str = Field(default="database.log", description="Database log file name")
    log_slow_queries: bool = Field(default=True, description="Log slow database queries")
    slow_query_threshold_ms: int = Field(default=1000, ge=100, le=60000, description="Slow query threshold in milliseconds")
    
    # Network Logging
    enable_network_logging: bool = Field(default=False, description="Enable network request logging")
    network_log_filename: str = Field(default="network.log", description="Network log file name")
    log_request_headers: bool = Field(default=False, description="Log HTTP request headers")
    log_response_headers: bool = Field(default=False, description="Log HTTP response headers")
    
    # Log Retention
    log_retention_days: int = Field(default=30, ge=1, le=365, description="Log retention period in days")
    enable_log_compression: bool = Field(default=True, description="Enable log file compression")
    
    # Remote Logging
    enable_remote_logging: bool = Field(default=False, description="Enable remote logging")
    remote_log_host: Optional[str] = Field(default=None, description="Remote log server host")
    remote_log_port: Optional[int] = Field(default=None, ge=1, le=65535, description="Remote log server port")
    remote_log_protocol: str = Field(default="TCP", description="Remote logging protocol")
    
    # Sensitive Data
    mask_sensitive_data: bool = Field(default=True, description="Mask sensitive data in logs")
    sensitive_fields: List[str] = Field(
        default=["password", "token", "secret", "key", "auth", "credential"],
        description="Fields to mask in logs"
    )
    
    class Config:
        env_prefix = "LOG_"
        case_sensitive = False
    
    @validator("log_level", "console_log_level", "error_log_level")
    def validate_log_levels(cls, v):
        """Validate log levels."""
        allowed_levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()
    
    @validator("component_log_levels")
    def validate_component_log_levels(cls, v):
        """Validate component log levels."""
        allowed_levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
        for component, level in v.items():
            if level.upper() not in allowed_levels:
                raise ValueError(f"Log level for {component} must be one of: {allowed_levels}")
            v[component] = level.upper()
        return v
    
    @validator("remote_log_protocol")
    def validate_remote_protocol(cls, v):
        """Validate remote logging protocol."""
        allowed_protocols = ["TCP", "UDP", "HTTP", "HTTPS"]
        if v.upper() not in allowed_protocols:
            raise ValueError(f"Remote log protocol must be one of: {allowed_protocols}")
        return v.upper()
    
    @validator("log_directory")
    def validate_log_directory(cls, v):
        """Ensure log directory exists."""
        if v and not os.path.isabs(v):
            v = os.path.abspath(v)
        os.makedirs(v, exist_ok=True)
        return v
    
    def get_log_level(self, development_mode: bool = False) -> str:
        """Get appropriate log level based on environment."""
        if development_mode:
            return "DEBUG"
        return self.log_level
    
    def get_file_handler_config(self) -> dict:
        """Get file handler configuration."""
        return {
            "enabled": self.enable_file_logging,
            "directory": self.log_directory,
            "filename": self.log_filename,
            "max_size_mb": self.max_log_size_mb,
            "backup_count": self.backup_count,
            "format": self.log_format,
            "date_format": self.date_format,
        }
    
    def get_console_handler_config(self) -> dict:
        """Get console handler configuration."""
        return {
            "enabled": self.enable_console_logging,
            "level": self.console_log_level,
            "colored": self.colored_console,
            "format": self.log_format,
            "date_format": self.date_format,
        }
    
    def get_json_handler_config(self) -> dict:
        """Get JSON handler configuration."""
        return {
            "enabled": self.enable_json_logging,
            "directory": self.log_directory,
            "filename": self.json_log_filename,
            "max_size_mb": self.max_log_size_mb,
            "backup_count": self.backup_count,
        }
    
    def get_error_handler_config(self) -> dict:
        """Get error handler configuration."""
        return {
            "enabled": self.enable_error_logging,
            "directory": self.log_directory,
            "filename": self.error_log_filename,
            "level": self.error_log_level,
            "max_size_mb": self.max_log_size_mb,
            "backup_count": self.backup_count,
        }
    
    def get_audit_handler_config(self) -> dict:
        """Get audit handler configuration."""
        return {
            "enabled": self.enable_audit_logging,
            "directory": self.log_directory,
            "filename": self.audit_log_filename,
            "events": self.audit_events,
            "max_size_mb": self.max_log_size_mb,
            "backup_count": self.backup_count,
        }
    
    def get_security_handler_config(self) -> dict:
        """Get security handler configuration."""
        return {
            "enabled": self.enable_security_logging,
            "directory": self.log_directory,
            "filename": self.security_log_filename,
            "log_failed_logins": self.log_failed_logins,
            "log_suspicious_activity": self.log_suspicious_activity,
            "max_size_mb": self.max_log_size_mb,
            "backup_count": self.backup_count,
        }
    
    def get_performance_handler_config(self) -> dict:
        """Get performance handler configuration."""
        return {
            "enabled": self.enable_performance_logging,
            "directory": self.log_directory,
            "filename": self.performance_log_filename,
            "threshold_ms": self.slow_operation_threshold_ms,
            "max_size_mb": self.max_log_size_mb,
            "backup_count": self.backup_count,
        }
    
    def get_database_handler_config(self) -> dict:
        """Get database handler configuration."""
        return {
            "enabled": self.enable_database_logging,
            "directory": self.log_directory,
            "filename": self.database_log_filename,
            "log_slow_queries": self.log_slow_queries,
            "slow_query_threshold_ms": self.slow_query_threshold_ms,
            "max_size_mb": self.max_log_size_mb,
            "backup_count": self.backup_count,
        }
    
    def get_remote_handler_config(self) -> dict:
        """Get remote handler configuration."""
        return {
            "enabled": self.enable_remote_logging,
            "host": self.remote_log_host,
            "port": self.remote_log_port,
            "protocol": self.remote_log_protocol,
        }
    
    def should_mask_field(self, field_name: str) -> bool:
        """Check if field should be masked in logs."""
        if not self.mask_sensitive_data:
            return False
        
        field_lower = field_name.lower()
        return any(sensitive in field_lower for sensitive in self.sensitive_fields)
    
    def mask_sensitive_value(self, value: str) -> str:
        """Mask sensitive value for logging."""
        if len(value) <= 4:
            return "*" * len(value)
        return value[:2] + "*" * (len(value) - 4) + value[-2:]
    
    def get_component_log_level(self, component: str) -> str:
        """Get log level for specific component."""
        return self.component_log_levels.get(component, self.log_level)

