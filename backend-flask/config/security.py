"""
Security Configuration

Centralized security configuration for the Industrial Vision Application.
"""

import secrets
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class SecurityConfig(BaseModel):
    """Security configuration settings."""
    
    # JWT Settings
    jwt_secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(default=30, ge=1, le=1440, description="JWT access token expiration in minutes")
    jwt_refresh_token_expire_days: int = Field(default=7, ge=1, le=30, description="JWT refresh token expiration in days")
    
    # Password Settings
    password_min_length: int = Field(default=8, ge=4, le=128, description="Minimum password length")
    password_require_uppercase: bool = Field(default=True, description="Require uppercase letters in password")
    password_require_lowercase: bool = Field(default=True, description="Require lowercase letters in password")
    password_require_numbers: bool = Field(default=True, description="Require numbers in password")
    password_require_special: bool = Field(default=True, description="Require special characters in password")
    password_hash_rounds: int = Field(default=12, ge=4, le=20, description="Password hash rounds (bcrypt)")
    
    # Session Settings
    session_timeout_minutes: int = Field(default=60, ge=5, le=1440, description="Session timeout in minutes")
    max_concurrent_sessions: int = Field(default=5, ge=1, le=100, description="Maximum concurrent sessions per user")
    session_cookie_secure: bool = Field(default=False, description="Secure session cookies (HTTPS only)")
    session_cookie_httponly: bool = Field(default=True, description="HTTP-only session cookies")
    session_cookie_samesite: str = Field(default="lax", description="SameSite cookie attribute")
    
    # API Security
    api_key_enabled: bool = Field(default=False, description="Enable API key authentication")
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    api_keys: List[str] = Field(default=[], description="Valid API keys")
    
    # Rate Limiting
    enable_rate_limiting: bool = Field(default=False, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=60, ge=1, le=1000, description="Rate limit per minute per IP")
    rate_limit_burst: int = Field(default=10, ge=1, le=100, description="Rate limit burst allowance")
    rate_limit_window: int = Field(default=60, ge=1, le=3600, description="Rate limit window in seconds")
    
    # IP Filtering
    enable_ip_whitelist: bool = Field(default=False, description="Enable IP whitelist")
    ip_whitelist: List[str] = Field(default=[], description="Allowed IP addresses/ranges")
    enable_ip_blacklist: bool = Field(default=False, description="Enable IP blacklist")
    ip_blacklist: List[str] = Field(default=[], description="Blocked IP addresses/ranges")
    
    # HTTPS Settings
    force_https: bool = Field(default=False, description="Force HTTPS redirects")
    hsts_enabled: bool = Field(default=False, description="Enable HTTP Strict Transport Security")
    hsts_max_age: int = Field(default=31536000, ge=0, description="HSTS max age in seconds")
    hsts_include_subdomains: bool = Field(default=False, description="Include subdomains in HSTS")
    
    # Content Security
    enable_csrf_protection: bool = Field(default=False, description="Enable CSRF protection")
    csrf_secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), description="CSRF secret key")
    enable_xss_protection: bool = Field(default=True, description="Enable XSS protection headers")
    enable_content_type_nosniff: bool = Field(default=True, description="Enable content type nosniff header")
    enable_frame_options: bool = Field(default=True, description="Enable X-Frame-Options header")
    frame_options_value: str = Field(default="DENY", description="X-Frame-Options header value")
    
    # Audit and Logging
    enable_audit_logging: bool = Field(default=True, description="Enable security audit logging")
    log_failed_logins: bool = Field(default=True, description="Log failed login attempts")
    log_privilege_escalation: bool = Field(default=True, description="Log privilege escalation attempts")
    max_failed_login_attempts: int = Field(default=5, ge=1, le=100, description="Maximum failed login attempts before lockout")
    account_lockout_duration_minutes: int = Field(default=15, ge=1, le=1440, description="Account lockout duration in minutes")
    
    # Encryption
    encryption_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), description="Data encryption key")
    encryption_algorithm: str = Field(default="AES-256-GCM", description="Encryption algorithm")
    
    # File Upload Security
    max_file_size_mb: int = Field(default=100, ge=1, le=1000, description="Maximum file upload size in MB")
    allowed_file_extensions: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".csv", ".json", ".xml"],
        description="Allowed file extensions"
    )
    scan_uploaded_files: bool = Field(default=False, description="Scan uploaded files for malware")
    
    # Database Security
    enable_sql_injection_protection: bool = Field(default=True, description="Enable SQL injection protection")
    enable_query_logging: bool = Field(default=False, description="Enable database query logging")
    mask_sensitive_data: bool = Field(default=True, description="Mask sensitive data in logs")
    
    class Config:
        env_prefix = "SECURITY_"
        case_sensitive = False
    
    @validator("jwt_algorithm")
    def validate_jwt_algorithm(cls, v):
        """Validate JWT algorithm."""
        allowed_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
        if v not in allowed_algorithms:
            raise ValueError(f"JWT algorithm must be one of: {allowed_algorithms}")
        return v
    
    @validator("session_cookie_samesite")
    def validate_samesite(cls, v):
        """Validate SameSite cookie attribute."""
        allowed_values = ["strict", "lax", "none"]
        if v.lower() not in allowed_values:
            raise ValueError(f"SameSite must be one of: {allowed_values}")
        return v.lower()
    
    @validator("frame_options_value")
    def validate_frame_options(cls, v):
        """Validate X-Frame-Options value."""
        allowed_values = ["DENY", "SAMEORIGIN"]
        if v.upper() not in allowed_values and not v.upper().startswith("ALLOW-FROM"):
            raise ValueError(f"Frame options must be one of: {allowed_values} or ALLOW-FROM uri")
        return v.upper()
    
    @validator("allowed_file_extensions")
    def validate_file_extensions(cls, v):
        """Validate file extensions format."""
        validated = []
        for ext in v:
            if not ext.startswith('.'):
                ext = '.' + ext
            validated.append(ext.lower())
        return validated
    
    def get_password_policy(self) -> dict:
        """Get password policy configuration."""
        return {
            "min_length": self.password_min_length,
            "require_uppercase": self.password_require_uppercase,
            "require_lowercase": self.password_require_lowercase,
            "require_numbers": self.password_require_numbers,
            "require_special": self.password_require_special,
            "hash_rounds": self.password_hash_rounds,
        }
    
    def get_jwt_config(self) -> dict:
        """Get JWT configuration."""
        return {
            "secret_key": self.jwt_secret_key,
            "algorithm": self.jwt_algorithm,
            "access_token_expire_minutes": self.jwt_access_token_expire_minutes,
            "refresh_token_expire_days": self.jwt_refresh_token_expire_days,
        }
    
    def get_session_config(self) -> dict:
        """Get session configuration."""
        return {
            "timeout_minutes": self.session_timeout_minutes,
            "max_concurrent": self.max_concurrent_sessions,
            "cookie_secure": self.session_cookie_secure,
            "cookie_httponly": self.session_cookie_httponly,
            "cookie_samesite": self.session_cookie_samesite,
        }
    
    def get_rate_limit_config(self) -> dict:
        """Get rate limiting configuration."""
        return {
            "enabled": self.enable_rate_limiting,
            "per_minute": self.rate_limit_per_minute,
            "burst": self.rate_limit_burst,
            "window": self.rate_limit_window,
        }
    
    def get_security_headers(self) -> dict:
        """Get security headers configuration."""
        headers = {}
        
        if self.enable_xss_protection:
            headers["X-XSS-Protection"] = "1; mode=block"
        
        if self.enable_content_type_nosniff:
            headers["X-Content-Type-Options"] = "nosniff"
        
        if self.enable_frame_options:
            headers["X-Frame-Options"] = self.frame_options_value
        
        if self.hsts_enabled:
            hsts_value = f"max-age={self.hsts_max_age}"
            if self.hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            headers["Strict-Transport-Security"] = hsts_value
        
        return headers
    
    def get_file_upload_config(self) -> dict:
        """Get file upload security configuration."""
        return {
            "max_size_mb": self.max_file_size_mb,
            "allowed_extensions": self.allowed_file_extensions,
            "scan_files": self.scan_uploaded_files,
        }
    
    def is_file_allowed(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        import os
        _, ext = os.path.splitext(filename.lower())
        return ext in self.allowed_file_extensions
    
    def validate_password(self, password: str) -> tuple[bool, List[str]]:
        """Validate password against policy."""
        errors = []
        
        if len(password) < self.password_min_length:
            errors.append(f"Password must be at least {self.password_min_length} characters long")
        
        if self.password_require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.password_require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.password_require_numbers and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if self.password_require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors

