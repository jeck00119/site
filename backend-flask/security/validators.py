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
    
    def validate_algorithm_property(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Validate algorithm property values with centralized logic.
        
        Args:
            key: Property name (e.g., 'golden_position', 'graphics')
            value: Property value to validate
            
        Returns:
            Dict with 'valid', 'error_message', and 'sanitized_value' keys
        """
        try:
            # Specific validation rules for algorithm properties
            validation_rules = {
                'golden_position': self._validate_golden_position,
                'graphics': self._validate_graphics,
                'model_path': self._validate_model_path,
                'confidence_threshold': self._validate_confidence_threshold,
                'iou_threshold': self._validate_iou_threshold,
                'reference_point_idx': self._validate_reference_point_idx,
            }
            
            # Get validator function or use generic validation
            validator = validation_rules.get(key, self._validate_generic_algorithm_property)
            
            return validator(value)
            
        except Exception as e:
            self.logger.error(f"Algorithm property validation error for {key}: {e}")
            return {
                'valid': False,
                'error_message': f"Validation failed for property '{key}': {str(e)}",
                'sanitized_value': None
            }
    
    def _validate_golden_position(self, value: Any) -> Dict[str, Any]:
        """Validate golden_position property."""
        try:
            # Must be a list of exactly 2 numeric values
            if not isinstance(value, (list, tuple)):
                return {
                    'valid': False,
                    'error_message': f"golden_position must be a list or tuple, got {type(value).__name__}",
                    'sanitized_value': None
                }
            
            if len(value) != 2:
                return {
                    'valid': False,
                    'error_message': f"golden_position must have exactly 2 values, got {len(value)}",
                    'sanitized_value': None
                }
            
            # Convert to list and validate numeric values
            try:
                sanitized = [float(x) for x in value]
            except (ValueError, TypeError):
                return {
                    'valid': False,
                    'error_message': "golden_position values must be numeric",
                    'sanitized_value': None
                }
            
            return {
                'valid': True,
                'error_message': None,
                'sanitized_value': sanitized
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error_message': f"golden_position validation error: {str(e)}",
                'sanitized_value': None
            }
    
    def _validate_graphics(self, value: Any) -> Dict[str, Any]:
        """Validate graphics property."""
        try:
            if not isinstance(value, list):
                return {
                    'valid': False,
                    'error_message': f"graphics must be a list, got {type(value).__name__}",
                    'sanitized_value': None
                }
            
            # Basic validation - each graphic should be a dict
            for i, graphic in enumerate(value):
                if not isinstance(graphic, dict):
                    return {
                        'valid': False,
                        'error_message': f"graphics[{i}] must be a dictionary, got {type(graphic).__name__}",
                        'sanitized_value': None
                    }
            
            return {
                'valid': True,
                'error_message': None,
                'sanitized_value': value
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error_message': f"graphics validation error: {str(e)}",
                'sanitized_value': None
            }
    
    def _validate_model_path(self, value: Any) -> Dict[str, Any]:
        """Validate model_path property."""
        try:
            if not isinstance(value, str):
                return {
                    'valid': False,
                    'error_message': f"model_path must be a string, got {type(value).__name__}",
                    'sanitized_value': None
                }
            
            # Sanitize the path for security
            sanitized = self._sanitize_filename(value)
            
            return {
                'valid': True,
                'error_message': None,
                'sanitized_value': sanitized
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error_message': f"model_path validation error: {str(e)}",
                'sanitized_value': None
            }
    
    def _validate_confidence_threshold(self, value: Any) -> Dict[str, Any]:
        """Validate confidence_threshold property."""
        try:
            try:
                float_value = float(value)
            except (ValueError, TypeError):
                return {
                    'valid': False,
                    'error_message': "confidence_threshold must be numeric",
                    'sanitized_value': None
                }
            
            if not 0.0 <= float_value <= 1.0:
                return {
                    'valid': False,
                    'error_message': "confidence_threshold must be between 0.0 and 1.0",
                    'sanitized_value': None
                }
            
            return {
                'valid': True,
                'error_message': None,
                'sanitized_value': float_value
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error_message': f"confidence_threshold validation error: {str(e)}",
                'sanitized_value': None
            }
    
    def _validate_iou_threshold(self, value: Any) -> Dict[str, Any]:
        """Validate iou_threshold property."""
        try:
            try:
                float_value = float(value)
            except (ValueError, TypeError):
                return {
                    'valid': False,
                    'error_message': "iou_threshold must be numeric",
                    'sanitized_value': None
                }
            
            if not 0.0 <= float_value <= 1.0:
                return {
                    'valid': False,
                    'error_message': "iou_threshold must be between 0.0 and 1.0",
                    'sanitized_value': None
                }
            
            return {
                'valid': True,
                'error_message': None,
                'sanitized_value': float_value
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error_message': f"iou_threshold validation error: {str(e)}",
                'sanitized_value': None
            }
    
    def _validate_reference_point_idx(self, value: Any) -> Dict[str, Any]:
        """Validate reference_point_idx property."""
        try:
            try:
                int_value = int(value)
            except (ValueError, TypeError):
                return {
                    'valid': False,
                    'error_message': "reference_point_idx must be an integer",
                    'sanitized_value': None
                }
            
            if int_value < 0:
                return {
                    'valid': False,
                    'error_message': "reference_point_idx must be non-negative",
                    'sanitized_value': None
                }
            
            return {
                'valid': True,
                'error_message': None,
                'sanitized_value': int_value
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error_message': f"reference_point_idx validation error: {str(e)}",
                'sanitized_value': None
            }
    
    def _validate_generic_algorithm_property(self, value: Any) -> Dict[str, Any]:
        """Generic validation for unknown algorithm properties."""
        try:
            # Basic security check - no malicious content
            if isinstance(value, str):
                threats = self.detect_threats(value)
                if threats:
                    return {
                        'valid': False,
                        'error_message': f"Property contains potential security threats: {', '.join(threats)}",
                        'sanitized_value': None
                    }
                
                # Sanitize string values
                sanitized_value = self.sanitize_input(value, "html")
            else:
                sanitized_value = value
            
            return {
                'valid': True,
                'error_message': None,
                'sanitized_value': sanitized_value
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error_message': f"Generic validation error: {str(e)}",
                'sanitized_value': None
            }

