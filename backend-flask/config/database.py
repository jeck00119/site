"""
Database Configuration

Centralized database configuration for the Industrial Vision Application.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, validator


class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    
    # Database Type
    db_type: str = Field(default="sqlite", description="Database type (sqlite, postgresql, mysql)")
    
    # SQLite Configuration
    sqlite_path: str = Field(default="config_db", description="SQLite database directory path")
    sqlite_timeout: int = Field(default=30, ge=1, le=300, description="SQLite connection timeout")
    sqlite_check_same_thread: bool = Field(default=False, description="SQLite check same thread setting")
    
    # PostgreSQL Configuration (for future use)
    postgres_host: Optional[str] = Field(default=None, description="PostgreSQL host")
    postgres_port: int = Field(default=5432, ge=1, le=65535, description="PostgreSQL port")
    postgres_database: Optional[str] = Field(default=None, description="PostgreSQL database name")
    postgres_username: Optional[str] = Field(default=None, description="PostgreSQL username")
    postgres_password: Optional[str] = Field(default=None, description="PostgreSQL password")
    
    # MySQL Configuration (for future use)
    mysql_host: Optional[str] = Field(default=None, description="MySQL host")
    mysql_port: int = Field(default=3306, ge=1, le=65535, description="MySQL port")
    mysql_database: Optional[str] = Field(default=None, description="MySQL database name")
    mysql_username: Optional[str] = Field(default=None, description="MySQL username")
    mysql_password: Optional[str] = Field(default=None, description="MySQL password")
    
    # Connection Pool Settings
    pool_size: int = Field(default=10, ge=1, le=100, description="Database connection pool size")
    max_overflow: int = Field(default=20, ge=0, le=100, description="Maximum connection pool overflow")
    pool_timeout: int = Field(default=30, ge=1, le=300, description="Connection pool timeout")
    pool_recycle: int = Field(default=3600, ge=300, le=86400, description="Connection pool recycle time")
    
    # Performance Settings
    enable_query_logging: bool = Field(default=False, description="Enable SQL query logging")
    slow_query_threshold: float = Field(default=1.0, ge=0.1, le=60.0, description="Slow query threshold in seconds")
    enable_connection_pooling: bool = Field(default=True, description="Enable connection pooling")
    
    # Backup Settings
    enable_auto_backup: bool = Field(default=True, description="Enable automatic database backup")
    backup_interval_hours: int = Field(default=24, ge=1, le=168, description="Backup interval in hours")
    backup_retention_days: int = Field(default=30, ge=1, le=365, description="Backup retention period in days")
    backup_directory: str = Field(default="backups", description="Backup directory path")
    
    class Config:
        env_prefix = "DB_"
        case_sensitive = False
    
    @validator("db_type")
    def validate_db_type(cls, v):
        """Validate database type."""
        allowed_types = ["sqlite", "postgresql", "mysql"]
        if v.lower() not in allowed_types:
            raise ValueError(f"Database type must be one of: {allowed_types}")
        return v.lower()
    
    @validator("sqlite_path")
    def validate_sqlite_path(cls, v):
        """Ensure SQLite path exists."""
        if v and not os.path.isabs(v):
            # Convert relative path to absolute
            v = os.path.abspath(v)
        os.makedirs(v, exist_ok=True)
        return v
    
    def get_connection_url(self) -> str:
        """Get database connection URL based on configuration."""
        if self.db_type == "sqlite":
            return f"sqlite:///{self.sqlite_path}"
        
        elif self.db_type == "postgresql":
            if not all([self.postgres_host, self.postgres_database, self.postgres_username]):
                raise ValueError("PostgreSQL configuration incomplete")
            
            password_part = f":{self.postgres_password}" if self.postgres_password else ""
            return (f"postgresql://{self.postgres_username}{password_part}@"
                   f"{self.postgres_host}:{self.postgres_port}/{self.postgres_database}")
        
        elif self.db_type == "mysql":
            if not all([self.mysql_host, self.mysql_database, self.mysql_username]):
                raise ValueError("MySQL configuration incomplete")
            
            password_part = f":{self.mysql_password}" if self.mysql_password else ""
            return (f"mysql://{self.mysql_username}{password_part}@"
                   f"{self.mysql_host}:{self.mysql_port}/{self.mysql_database}")
        
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def get_sqlite_config(self) -> dict:
        """Get SQLite-specific configuration."""
        return {
            "path": self.sqlite_path,
            "timeout": self.sqlite_timeout,
            "check_same_thread": self.sqlite_check_same_thread
        }
    
    def get_pool_config(self) -> dict:
        """Get connection pool configuration."""
        return {
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle
        }
    
    def get_backup_config(self) -> dict:
        """Get backup configuration."""
        return {
            "enabled": self.enable_auto_backup,
            "interval_hours": self.backup_interval_hours,
            "retention_days": self.backup_retention_days,
            "directory": self.backup_directory
        }
    
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.db_type == "sqlite"
    
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return self.db_type == "postgresql"
    
    def is_mysql(self) -> bool:
        """Check if using MySQL database."""
        return self.db_type == "mysql"

