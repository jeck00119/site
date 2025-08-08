"""
Server Configuration

Centralized server configuration for the Industrial Vision Application.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ServerConfig(BaseModel):
    """Server configuration settings."""
    
    # Basic Server Settings
    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    workers: int = Field(default=1, ge=1, le=16, description="Number of worker processes")
    
    # Development Settings
    reload: bool = Field(default=False, description="Enable auto-reload in development")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # CORS Settings
    cors_allow_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173", 
            "http://localhost:5174",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:8080"
        ],
        description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow CORS credentials")
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        description="Allowed CORS methods"
    )
    cors_allow_headers: List[str] = Field(default=["*"], description="Allowed CORS headers")
    cors_expose_headers: List[str] = Field(
        default=["Auth-Token", "User-Data", "Token-Expiration", "Level", "Content-Disposition"],
        description="Exposed CORS headers"
    )
    
    # SSL/TLS Settings
    ssl_enabled: bool = Field(default=False, description="Enable SSL/TLS")
    ssl_cert_file: Optional[str] = Field(default=None, description="SSL certificate file path")
    ssl_key_file: Optional[str] = Field(default=None, description="SSL private key file path")
    ssl_ca_file: Optional[str] = Field(default=None, description="SSL CA file path")
    
    # Performance Settings
    max_request_size: int = Field(default=100 * 1024 * 1024, ge=1024, description="Maximum request size in bytes")  # 100MB
    request_timeout: int = Field(default=300, ge=1, le=3600, description="Request timeout in seconds")
    keep_alive_timeout: int = Field(default=5, ge=1, le=300, description="Keep-alive timeout in seconds")
    
    # Logging Settings
    access_log: bool = Field(default=True, description="Enable access logging")
    log_level: str = Field(default="info", description="Server log level")
    
    # Rate Limiting
    enable_rate_limiting: bool = Field(default=False, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, ge=1, le=10000, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, ge=1, le=3600, description="Rate limit window in seconds")
    
    # Health Check Settings
    health_check_enabled: bool = Field(default=True, description="Enable health check endpoint")
    health_check_path: str = Field(default="/health", description="Health check endpoint path")
    
    # Static Files
    static_files_enabled: bool = Field(default=True, description="Enable static file serving")
    static_files_directory: str = Field(default="static", description="Static files directory")
    static_files_path: str = Field(default="/static", description="Static files URL path")
    
    # WebSocket Settings
    websocket_enabled: bool = Field(default=True, description="Enable WebSocket support")
    websocket_ping_interval: int = Field(default=20, ge=5, le=300, description="WebSocket ping interval in seconds")
    websocket_ping_timeout: int = Field(default=10, ge=1, le=60, description="WebSocket ping timeout in seconds")
    websocket_max_connections: int = Field(default=100, ge=1, le=1000, description="Maximum WebSocket connections")
    
    class Config:
        env_prefix = "SERVER_"
        case_sensitive = False
    
    @field_validator("host")
    @classmethod
    def validate_host(cls, v):
        """Validate host address."""
        if v not in ["0.0.0.0", "127.0.0.1", "localhost"] and not v.startswith("192.168."):
            # Allow common local addresses and private network ranges
            import ipaddress
            try:
                ip = ipaddress.ip_address(v)
                if not (ip.is_private or ip.is_loopback):
                    raise ValueError("Host must be a private or loopback address")
            except ipaddress.AddressValueError:
                raise ValueError("Invalid host address format")
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed_levels = ["critical", "error", "warning", "info", "debug", "trace"]
        if v.lower() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.lower()
    
    @field_validator("ssl_cert_file", "ssl_key_file", "ssl_ca_file")
    @classmethod
    def validate_ssl_files(cls, v):
        """Validate SSL file paths."""
        if v is not None:
            import os
            if not os.path.exists(v):
                raise ValueError(f"SSL file not found: {v}")
        return v
    
    def get_cors_origins(self, development_mode: bool = False) -> List[str]:
        """Get CORS origins based on environment."""
        if development_mode:
            # In development, allow all localhost origins
            return ["*"]
        else:
            # In production, use specific origins
            return self.cors_allow_origins
    
    def get_server_url(self) -> str:
        """Get server URL."""
        protocol = "https" if self.ssl_enabled else "http"
        return f"{protocol}://{self.host}:{self.port}"
    
    def get_uvicorn_config(self) -> dict:
        """Get Uvicorn server configuration."""
        config = {
            "host": self.host,
            "port": self.port,
            "log_level": self.log_level,
            "access_log": self.access_log,
            "reload": self.reload,
            "workers": self.workers if not self.reload else 1,  # Workers > 1 not compatible with reload
            # Add graceful shutdown timeouts to prevent hanging
            "timeout_graceful_shutdown": 10,  # Force shutdown after 10 seconds
            "timeout_keep_alive": self.keep_alive_timeout,
        }
        
        if self.ssl_enabled and self.ssl_cert_file and self.ssl_key_file:
            config.update({
                "ssl_certfile": self.ssl_cert_file,
                "ssl_keyfile": self.ssl_key_file,
            })
            if self.ssl_ca_file:
                config["ssl_ca_certs"] = self.ssl_ca_file
        
        return config
    
    def get_cors_config(self, development_mode: bool = False) -> dict:
        """Get CORS middleware configuration."""
        return {
            "allow_origins": self.get_cors_origins(development_mode),
            "allow_credentials": self.cors_allow_credentials,
            "allow_methods": self.cors_allow_methods,
            "allow_headers": self.cors_allow_headers,
            "expose_headers": self.cors_expose_headers,
        }
    
    def get_rate_limit_config(self) -> dict:
        """Get rate limiting configuration."""
        return {
            "enabled": self.enable_rate_limiting,
            "requests": self.rate_limit_requests,
            "window": self.rate_limit_window,
        }
    
    def get_websocket_config(self) -> dict:
        """Get WebSocket configuration."""
        return {
            "enabled": self.websocket_enabled,
            "ping_interval": self.websocket_ping_interval,
            "ping_timeout": self.websocket_ping_timeout,
            "max_connections": self.websocket_max_connections,
        }

