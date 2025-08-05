"""
Encryption Manager

Provides data encryption and decryption capabilities for sensitive data.
"""

import base64
import hashlib
import secrets
from typing import Union, Optional
import logging

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config.settings import get_settings
from src.metaclasses.singleton import Singleton


class EncryptionManager(metaclass=Singleton):
    """
    Manages encryption and decryption of sensitive data.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.security_config = self.settings.security
        self.logger = logging.getLogger(__name__)
        
        # Initialize encryption key
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption with the configured key."""
        try:
            # Use the configured encryption key or generate one
            key = self.security_config.encryption_key
            
            # Derive a proper Fernet key from the configured key
            derived_key = self._derive_key(key.encode())
            self._fernet = Fernet(derived_key)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize encryption: {e}")
            raise
    
    def _derive_key(self, password: bytes, salt: Optional[bytes] = None) -> bytes:
        """Derive a Fernet-compatible key from password."""
        if salt is None:
            # Use a fixed salt for consistency (in production, consider using per-data salts)
            salt = b'industrial_vision_salt_2024'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_string(self, plaintext: str) -> str:
        """Encrypt a string and return base64-encoded result."""
        try:
            if not plaintext:
                return ""
            
            # Encrypt the data
            encrypted_data = self._fernet.encrypt(plaintext.encode('utf-8'))
            
            # Return base64-encoded string
            return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"String encryption failed: {e}")
            raise
    
    def decrypt_string(self, encrypted_data: str) -> str:
        """Decrypt a base64-encoded encrypted string."""
        try:
            if not encrypted_data:
                return ""
            
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt the data
            decrypted_data = self._fernet.decrypt(encrypted_bytes)
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"String decryption failed: {e}")
            raise
    
    def encrypt_bytes(self, data: bytes) -> bytes:
        """Encrypt bytes data."""
        try:
            return self._fernet.encrypt(data)
        except Exception as e:
            self.logger.error(f"Bytes encryption failed: {e}")
            raise
    
    def decrypt_bytes(self, encrypted_data: bytes) -> bytes:
        """Decrypt bytes data."""
        try:
            return self._fernet.decrypt(encrypted_data)
        except Exception as e:
            self.logger.error(f"Bytes decryption failed: {e}")
            raise
    
    def encrypt_dict(self, data: dict) -> str:
        """Encrypt a dictionary as JSON string."""
        try:
            import json
            json_string = json.dumps(data, separators=(',', ':'))
            return self.encrypt_string(json_string)
        except Exception as e:
            self.logger.error(f"Dictionary encryption failed: {e}")
            raise
    
    def decrypt_dict(self, encrypted_data: str) -> dict:
        """Decrypt an encrypted dictionary."""
        try:
            import json
            json_string = self.decrypt_string(encrypted_data)
            return json.loads(json_string)
        except Exception as e:
            self.logger.error(f"Dictionary decryption failed: {e}")
            raise
    
    def hash_data(self, data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """Create a hash of the data."""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if algorithm == "sha256":
                hash_obj = hashlib.sha256(data)
            elif algorithm == "sha512":
                hash_obj = hashlib.sha512(data)
            elif algorithm == "md5":
                hash_obj = hashlib.md5(data)
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Data hashing failed: {e}")
            raise
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure random token."""
        try:
            return secrets.token_urlsafe(length)
        except Exception as e:
            self.logger.error(f"Token generation failed: {e}")
            raise
    
    def generate_api_key(self, prefix: str = "aoi") -> str:
        """Generate a secure API key with prefix."""
        try:
            random_part = secrets.token_urlsafe(32)
            return f"{prefix}_{random_part}"
        except Exception as e:
            self.logger.error(f"API key generation failed: {e}")
            raise
    
    def encrypt_sensitive_fields(self, data: dict, sensitive_fields: list = None) -> dict:
        """Encrypt sensitive fields in a dictionary."""
        try:
            if sensitive_fields is None:
                sensitive_fields = self.security_config.sensitive_fields
            
            encrypted_data = data.copy()
            
            for field in sensitive_fields:
                if field in encrypted_data and encrypted_data[field]:
                    # Check if field name contains sensitive keywords
                    field_lower = field.lower()
                    if any(keyword in field_lower for keyword in ["password", "secret", "key", "token"]):
                        encrypted_data[field] = self.encrypt_string(str(encrypted_data[field]))
            
            return encrypted_data
            
        except Exception as e:
            self.logger.error(f"Sensitive field encryption failed: {e}")
            raise
    
    def decrypt_sensitive_fields(self, data: dict, sensitive_fields: list = None) -> dict:
        """Decrypt sensitive fields in a dictionary."""
        try:
            if sensitive_fields is None:
                sensitive_fields = self.security_config.sensitive_fields
            
            decrypted_data = data.copy()
            
            for field in sensitive_fields:
                if field in decrypted_data and decrypted_data[field]:
                    try:
                        # Try to decrypt the field
                        decrypted_data[field] = self.decrypt_string(decrypted_data[field])
                    except Exception:
                        # If decryption fails, assume it's not encrypted
                        pass
            
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Sensitive field decryption failed: {e}")
            raise
    
    def create_checksum(self, data: Union[str, bytes]) -> str:
        """Create a checksum for data integrity verification."""
        try:
            return self.hash_data(data, "sha256")
        except Exception as e:
            self.logger.error(f"Checksum creation failed: {e}")
            raise
    
    def verify_checksum(self, data: Union[str, bytes], expected_checksum: str) -> bool:
        """Verify data integrity using checksum."""
        try:
            actual_checksum = self.create_checksum(data)
            return actual_checksum == expected_checksum
        except Exception as e:
            self.logger.error(f"Checksum verification failed: {e}")
            return False
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """Encrypt a file."""
        try:
            if output_path is None:
                output_path = file_path + ".encrypted"
            
            with open(file_path, 'rb') as infile:
                data = infile.read()
            
            encrypted_data = self.encrypt_bytes(data)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(encrypted_data)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"File encryption failed: {e}")
            raise
    
    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """Decrypt a file."""
        try:
            if output_path is None:
                if encrypted_file_path.endswith('.encrypted'):
                    output_path = encrypted_file_path[:-10]  # Remove .encrypted
                else:
                    output_path = encrypted_file_path + ".decrypted"
            
            with open(encrypted_file_path, 'rb') as infile:
                encrypted_data = infile.read()
            
            decrypted_data = self.decrypt_bytes(encrypted_data)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(decrypted_data)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"File decryption failed: {e}")
            raise
    
    def secure_delete(self, data: Union[str, bytes, dict]) -> None:
        """Securely delete sensitive data from memory."""
        try:
            if isinstance(data, str):
                # Overwrite string data (limited effectiveness in Python)
                data = "0" * len(data)
            elif isinstance(data, dict):
                # Clear dictionary
                data.clear()
            elif isinstance(data, bytes):
                # For bytes, we can't truly overwrite in Python
                # This is more of a symbolic operation
                pass
            
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            self.logger.error(f"Secure delete failed: {e}")
    
    def rotate_encryption_key(self, new_key: str) -> None:
        """Rotate the encryption key (requires re-encrypting all data)."""
        try:
            # Store old fernet for decryption
            old_fernet = self._fernet
            
            # Initialize with new key
            derived_key = self._derive_key(new_key.encode())
            self._fernet = Fernet(derived_key)
            
            # Update configuration
            self.security_config.encryption_key = new_key
            
            self.logger.info("Encryption key rotated successfully")
            
            # Note: In a real implementation, you would need to:
            # 1. Decrypt all encrypted data with old key
            # 2. Re-encrypt with new key
            # 3. Update database records
            
        except Exception as e:
            self.logger.error(f"Key rotation failed: {e}")
            raise

