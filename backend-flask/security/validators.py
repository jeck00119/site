"""
Security Validators

Provides input validation and sanitization for security purposes.
"""

import re
import html
import urllib.parse
from typing import Any, Dict, List, Optional, Union
import logging

from config.settings import get_settings


class SecurityValidator:
    """
    Comprehensive security validation and sanitization.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.security_config = self.settings.security
        self.logger = logging.getLogger(__name__)
        
        # Common patterns for validation
        self.patterns = {
            "email": re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            "username": re.compile(r'^[a-zA-Z0-9_-]{3,50}$'),
            "filename": re.compile(r'^[a-zA-Z0-9._-]+$'),
            "ip_address": re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'),
            "sql_injection": re.compile(r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)', re.IGNORECASE),
            "xss": re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            "path_traversal": re.compile(r'\.\.[\\/]'),
            "command_injection": re.compile(r'[;&|`$(){}\[\]<>]'),
        }
    
    def validate_input(self, value: Any, validation_type: str, **kwargs) -> bool:
        """Validate input based on type."""
        try:
            if value is None:
                return kwargs.get('allow_none', False)
            
            if not isinstance(value, str):
                value = str(value)
            
            # Length validation
            min_length = kwargs.get('min_length', 0)
            max_length = kwargs.get('max_length', 1000)
            
            if len(value) < min_length or len(value) > max_length:
                return False
            
            # Type-specific validation
            if validation_type == "email":
                return self._validate_email(value)
            elif validation_type == "username":
                return self._validate_username(value)
            elif validation_type == "password":
                return self._validate_password(value)
            elif validation_type == "filename":
                return self._validate_filename(value)
            elif validation_type == "ip_address":
                return self._validate_ip_address(value)
            elif validation_type == "url":
                return self._validate_url(value)
            elif validation_type == "safe_string":
                return self._validate_safe_string(value)
            elif validation_type == "numeric":
                return self._validate_numeric(value, **kwargs)
            else:
                self.logger.warning(f"Unknown validation type: {validation_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Validation error for {validation_type}: {e}")
            return False
    
    def sanitize_input(self, value: Any, sanitization_type: str = "html") -> str:
        """Sanitize input to prevent security issues."""
        try:
            if value is None:
                return ""
            
            if not isinstance(value, str):
                value = str(value)
            
            if sanitization_type == "html":
                return self._sanitize_html(value)
            elif sanitization_type == "sql":
                return self._sanitize_sql(value)
            elif sanitization_type == "filename":
                return self._sanitize_filename(value)
            elif sanitization_type == "url":
                return self._sanitize_url(value)
            elif sanitization_type == "command":
                return self._sanitize_command(value)
            else:
                # Default: basic sanitization
                return self._sanitize_basic(value)
                
        except Exception as e:
            self.logger.error(f"Sanitization error for {sanitization_type}: {e}")
            return ""
    
    def detect_threats(self, value: str) -> List[str]:
        """Detect potential security threats in input."""
        threats = []
        
        try:
            # SQL Injection
            if self.patterns["sql_injection"].search(value):
                threats.append("sql_injection")
            
            # XSS
            if self.patterns["xss"].search(value):
                threats.append("xss")
            
            # Path Traversal
            if self.patterns["path_traversal"].search(value):
                threats.append("path_traversal")
            
            # Command Injection
            if self.patterns["command_injection"].search(value):
                threats.append("command_injection")
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r'javascript:',
                r'data:',
                r'vbscript:',
                r'onload=',
                r'onerror=',
                r'eval\(',
                r'document\.cookie',
                r'window\.location'
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    threats.append("suspicious_content")
                    break
            
        except Exception as e:
            self.logger.error(f"Threat detection error: {e}")
        
        return threats
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format and ensure it's a @forvia email."""
        # First check basic email format
        if not self.patterns["email"].match(email):
            return False
        
        # Then check if it's a @forvia email
        return '@forvia' in email.lower()
    
    def _validate_username(self, username: str) -> bool:
        """Validate username format."""
        return bool(self.patterns["username"].match(username))
    
    def _validate_password(self, password: str) -> bool:
        """Validate password against security policy."""
        is_valid, _ = self.security_config.validate_password(password)
        return is_valid
    
    def _validate_filename(self, filename: str) -> bool:
        """Validate filename for security."""
        # Check basic pattern
        if not self.patterns["filename"].match(filename):
            return False
        
        # Check file extension
        if '.' in filename:
            extension = '.' + filename.split('.')[-1].lower()
            return self.security_config.is_file_allowed(filename)
        
        return True
    
    def _validate_ip_address(self, ip: str) -> bool:
        """Validate IP address format."""
        return bool(self.patterns["ip_address"].match(ip))
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format and safety."""
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Only allow safe schemes
            safe_schemes = ['http', 'https', 'ftp', 'ftps']
            if parsed.scheme.lower() not in safe_schemes:
                return False
            
            # Check for suspicious patterns
            if any(threat in url.lower() for threat in ['javascript:', 'data:', 'vbscript:']):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_safe_string(self, value: str) -> bool:
        """Validate string for general safety."""
        # Check for threats
        threats = self.detect_threats(value)
        return len(threats) == 0
    
    def _validate_numeric(self, value: str, **kwargs) -> bool:
        """Validate numeric input."""
        try:
            if kwargs.get('integer_only', False):
                int(value)
            else:
                float(value)
            
            # Range validation
            if 'min_value' in kwargs or 'max_value' in kwargs:
                num_value = float(value)
                if 'min_value' in kwargs and num_value < kwargs['min_value']:
                    return False
                if 'max_value' in kwargs and num_value > kwargs['max_value']:
                    return False
            
            return True
            
        except ValueError:
            return False
    
    def _sanitize_html(self, value: str) -> str:
        """Sanitize HTML content."""
        # Escape HTML entities
        sanitized = html.escape(value)
        
        # Remove potentially dangerous tags
        dangerous_tags = [
            r'<script[^>]*>.*?</script>',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'<form[^>]*>.*?</form>',
        ]
        
        for tag_pattern in dangerous_tags:
            sanitized = re.sub(tag_pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        return sanitized
    
    def _sanitize_sql(self, value: str) -> str:
        """Sanitize SQL input."""
        # Escape single quotes
        sanitized = value.replace("'", "''")
        
        # Remove SQL keywords (basic approach)
        sql_keywords = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
            'ALTER', 'EXEC', 'EXECUTE', 'UNION', 'SCRIPT'
        ]
        
        for keyword in sql_keywords:
            sanitized = re.sub(rf'\b{keyword}\b', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename."""
        # Remove path separators
        sanitized = filename.replace('/', '').replace('\\', '')
        
        # Remove dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            max_name_length = 255 - len(ext) - 1 if ext else 255
            sanitized = name[:max_name_length] + ('.' + ext if ext else '')
        
        return sanitized
    
    def _sanitize_url(self, url: str) -> str:
        """Sanitize URL."""
        # URL encode the URL
        return urllib.parse.quote(url, safe=':/?#[]@!$&\'()*+,;=')
    
    def _sanitize_command(self, command: str) -> str:
        """Sanitize command input."""
        # Remove dangerous characters
        dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '{', '}', '[', ']', '<', '>']
        sanitized = command
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized
    
    def _sanitize_basic(self, value: str) -> str:
        """Basic sanitization."""
        # Remove null bytes
        sanitized = value.replace('\0', '')
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
        
        return sanitized
    
    def validate_file_upload(self, filename: str, content: bytes) -> Dict[str, Any]:
        """Validate file upload for security."""
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Validate filename
            if not self._validate_filename(filename):
                result["valid"] = False
                result["errors"].append("Invalid filename")
            
            # Check file size
            file_size_mb = len(content) / (1024 * 1024)
            if file_size_mb > self.security_config.max_file_size_mb:
                result["valid"] = False
                result["errors"].append(f"File too large: {file_size_mb:.1f}MB > {self.security_config.max_file_size_mb}MB")
            
            # Check file extension
            if not self.security_config.is_file_allowed(filename):
                result["valid"] = False
                result["errors"].append("File type not allowed")
            
            # Basic content validation
            if self._detect_malicious_content(content):
                result["valid"] = False
                result["errors"].append("Potentially malicious content detected")
            
        except Exception as e:
            self.logger.error(f"File validation error: {e}")
            result["valid"] = False
            result["errors"].append("File validation failed")
        
        return result
    
    def _detect_malicious_content(self, content: bytes) -> bool:
        """Detect potentially malicious content in files."""
        try:
            # Convert to string for pattern matching (first 1KB only)
            text_content = content[:1024].decode('utf-8', errors='ignore').lower()
            
            # Check for suspicious patterns
            malicious_patterns = [
                b'<script',
                b'javascript:',
                b'vbscript:',
                b'data:text/html',
                b'<?php',
                b'<%',
                b'eval(',
                b'exec(',
                b'system(',
                b'shell_exec(',
            ]
            
            for pattern in malicious_patterns:
                if pattern in content[:1024]:
                    return True
            
            return False
            
        except Exception:
            # If we can't analyze the content, be conservative
            return True


# Validation Decorators for Routes

import functools
from typing import Dict, Any, Callable
from fastapi import HTTPException, status

def validate_input(**validation_rules):
    """
    Decorator to validate route input parameters.
    
    Args:
        validation_rules: Mapping of parameter names to validation types
        
    Usage:
        @validate_input(email="email", username="username", password="password")
        async def create_user(email: str, username: str, password: str):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            validator = SecurityValidator()
            
            # Validate each specified parameter
            for param_name, validation_type in validation_rules.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    if not validator.validate_input(value, validation_type):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid {param_name}: {validation_type} validation failed"
                        )
                    
                    # Sanitize the input
                    sanitized = validator.sanitize_input(value)
                    kwargs[param_name] = sanitized
            
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            validator = SecurityValidator()
            
            # Validate each specified parameter
            for param_name, validation_type in validation_rules.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    if not validator.validate_input(value, validation_type):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid {param_name}: {validation_type} validation failed"
                        )
                    
                    # Sanitize the input
                    sanitized = validator.sanitize_input(value)
                    kwargs[param_name] = sanitized
            
            return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def validate_file_upload(allowed_types: list = None, max_size_mb: int = None):
    """
    Decorator to validate file uploads.
    
    Args:
        allowed_types: List of allowed file extensions
        max_size_mb: Maximum file size in MB
        
    Usage:
        @validate_file_upload(allowed_types=['.jpg', '.png'], max_size_mb=10)
        async def upload_image(file: UploadFile):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            validator = SecurityValidator()
            
            # Find file parameters
            for param_name, param_value in kwargs.items():
                if hasattr(param_value, 'filename') and hasattr(param_value, 'read'):
                    # This is a file upload
                    content = await param_value.read()
                    validation_result = validator.validate_file_upload(
                        param_value.filename, 
                        content,
                        allowed_types=allowed_types,
                        max_size_mb=max_size_mb
                    )
                    
                    if not validation_result["valid"]:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"File validation failed: {', '.join(validation_result['errors'])}"
                        )
                    
                    # Reset file pointer
                    param_value.file.seek(0)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def detect_security_threats(check_all_strings: bool = True):
    """
    Decorator to detect security threats in input parameters.
    
    Args:
        check_all_strings: If True, check all string parameters for threats
        
    Usage:
        @detect_security_threats()
        async def process_user_input(data: str):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            validator = SecurityValidator()
            
            if check_all_strings:
                for param_name, param_value in kwargs.items():
                    if isinstance(param_value, str):
                        threats = validator.detect_threats(param_value)
                        if threats:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Security threats detected in {param_name}: {', '.join(threats)}"
                            )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

