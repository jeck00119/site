"""
Authentication and Authorization Manager

Provides comprehensive authentication and authorization features.
"""

import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config.settings import get_settings
from .audit import AuditLogger
from src.metaclasses.singleton import Singleton


class TokenManager:
    """
    JWT Token management for authentication.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.security_config = self.settings.security
        self.logger = logging.getLogger(__name__)
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token."""
        try:
            # Token payload
            payload = {
                "sub": user_data["username"],
                "user_id": user_data.get("uid", user_data.get("id")),
                "level": user_data.get("level", "user"),
                "roles": user_data.get("roles", []),
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(
                    minutes=self.security_config.jwt_access_token_expire_minutes
                ),
                "type": "access"
            }
            
            # Create token
            token = jwt.encode(
                payload,
                self.security_config.jwt_secret_key,
                algorithm=self.security_config.jwt_algorithm
            )
            
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to create access token: {e}")
            raise HTTPException(status_code=500, detail="Token creation failed")
    
    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT refresh token."""
        try:
            payload = {
                "sub": user_data["username"],
                "user_id": user_data.get("uid", user_data.get("id")),
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(
                    days=self.security_config.jwt_refresh_token_expire_days
                ),
                "type": "refresh"
            }
            
            token = jwt.encode(
                payload,
                self.security_config.jwt_secret_key,
                algorithm=self.security_config.jwt_algorithm
            )
            
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to create refresh token: {e}")
            raise HTTPException(status_code=500, detail="Token creation failed")
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.security_config.jwt_secret_key,
                algorithms=[self.security_config.jwt_algorithm]
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Token expired")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            self.logger.error(f"Token verification failed: {e}")
            raise HTTPException(status_code=401, detail="Token verification failed")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token."""
        try:
            # Verify refresh token
            payload = self.verify_token(refresh_token, "refresh")
            
            # Create new access token
            user_data = {
                "username": payload["sub"],
                "uid": payload["user_id"],
                "level": payload.get("level", "user"),
                "roles": payload.get("roles", [])
            }
            
            return self.create_access_token(user_data)
            
        except Exception as e:
            self.logger.error(f"Token refresh failed: {e}")
            raise HTTPException(status_code=401, detail="Token refresh failed")


class PasswordManager:
    """
    Password hashing and validation.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.security_config = self.settings.security
        self.logger = logging.getLogger(__name__)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        try:
            # Validate password against policy
            is_valid, errors = self.security_config.validate_password(password)
            if not is_valid:
                raise ValueError(f"Password policy violation: {', '.join(errors)}")
            
            # Hash password
            salt = bcrypt.gensalt(rounds=self.security_config.password_hash_rounds)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            return hashed.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Password hashing failed: {e}")
            raise
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            self.logger.error(f"Password verification failed: {e}")
            return False
    
    def generate_secure_password(self, length: int = 12) -> str:
        """Generate a secure random password."""
        import string
        
        # Ensure minimum requirements
        chars = []
        
        if self.security_config.password_require_uppercase:
            chars.extend(string.ascii_uppercase)
        
        if self.security_config.password_require_lowercase:
            chars.extend(string.ascii_lowercase)
        
        if self.security_config.password_require_numbers:
            chars.extend(string.digits)
        
        if self.security_config.password_require_special:
            chars.extend("!@#$%^&*()_+-=[]{}|;:,.<>?")
        
        if not chars:
            chars = string.ascii_letters + string.digits
        
        # Generate password
        password = ''.join(secrets.choice(chars) for _ in range(length))
        
        # Validate generated password
        is_valid, _ = self.security_config.validate_password(password)
        if not is_valid:
            # Retry with longer length
            return self.generate_secure_password(length + 2)
        
        return password


class AuthManager(metaclass=Singleton):
    """
    Main authentication and authorization manager.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.security_config = self.settings.security
        self.logger = logging.getLogger(__name__)
        self.audit_logger = AuditLogger()
        
        self.token_manager = TokenManager()
        self.password_manager = PasswordManager()
        
        # Failed login tracking
        self.failed_login_attempts: Dict[str, List[datetime]] = {}
        self.locked_accounts: Dict[str, datetime] = {}
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """Authenticate user with username and password."""
        try:
            # Check if account is locked
            if self._is_account_locked(username):
                await self.audit_logger.log_authentication_event(
                    "login_attempt_locked",
                    username,
                    False,
                    request,
                    {"reason": "account_locked"}
                )
                raise HTTPException(
                    status_code=423,
                    detail="Account temporarily locked due to too many failed attempts"
                )
            
            # Get user from database (this would integrate with your user repository)
            user = await self._get_user_by_username(username)
            if not user:
                await self._record_failed_login(username, request)
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Verify password
            if not self.password_manager.verify_password(password, user["password"]):
                await self._record_failed_login(username, request)
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Clear failed login attempts on successful login
            self._clear_failed_login_attempts(username)
            
            # Create tokens
            access_token = self.token_manager.create_access_token(user)
            refresh_token = self.token_manager.create_refresh_token(user)
            
            # Log successful authentication
            await self.audit_logger.log_authentication_event(
                "login_success",
                username,
                True,
                request
            )
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": self.security_config.jwt_access_token_expire_minutes * 60,
                "user": {
                    "username": user["username"],
                    "level": user.get("level", "user"),
                    "roles": user.get("roles", [])
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            await self.audit_logger.log_authentication_event(
                "login_error",
                username,
                False,
                request,
                {"error": str(e)}
            )
            raise HTTPException(status_code=500, detail="Authentication failed")
    
    async def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user from database by username."""
        # This would integrate with your existing user repository
        # For now, return a placeholder implementation
        from repo.repositories import UsersRepository
        
        try:
            users_repo = UsersRepository()
            return users_repo.get_by_username(username)
        except Exception:
            return None
    
    def _is_account_locked(self, username: str) -> bool:
        """Check if account is currently locked."""
        if username in self.locked_accounts:
            lock_time = self.locked_accounts[username]
            unlock_time = lock_time + timedelta(
                minutes=self.security_config.account_lockout_duration_minutes
            )
            
            if datetime.utcnow() < unlock_time:
                return True
            else:
                # Unlock account
                del self.locked_accounts[username]
        
        return False
    
    async def _record_failed_login(self, username: str, request: Optional[Request] = None):
        """Record failed login attempt."""
        current_time = datetime.utcnow()
        
        if username not in self.failed_login_attempts:
            self.failed_login_attempts[username] = []
        
        self.failed_login_attempts[username].append(current_time)
        
        # Remove old attempts (older than 1 hour)
        cutoff_time = current_time - timedelta(hours=1)
        self.failed_login_attempts[username] = [
            attempt for attempt in self.failed_login_attempts[username]
            if attempt > cutoff_time
        ]
        
        # Check if account should be locked
        if len(self.failed_login_attempts[username]) >= self.security_config.max_failed_login_attempts:
            self.locked_accounts[username] = current_time
            
            await self.audit_logger.log_security_event(
                "account_locked",
                f"Account {username} locked due to too many failed login attempts",
                request,
                {"failed_attempts": len(self.failed_login_attempts[username])}
            )
        
        # Log failed attempt
        await self.audit_logger.log_authentication_event(
            "login_failure",
            username,
            False,
            request,
            {"failed_attempts": len(self.failed_login_attempts[username])}
        )
    
    def _clear_failed_login_attempts(self, username: str):
        """Clear failed login attempts for user."""
        if username in self.failed_login_attempts:
            del self.failed_login_attempts[username]
        
        if username in self.locked_accounts:
            del self.locked_accounts[username]
    
    def check_permission(
        self,
        user: Dict[str, Any],
        resource: str,
        action: str
    ) -> bool:
        """Check if user has permission for resource and action."""
        user_level = user.get("level", "user")
        user_roles = user.get("roles", [])
        
        # Admin has all permissions
        if user_level == "admin":
            return True
        
        # Define permission matrix
        permissions = {
            "cnc": {
                "read": ["user", "operator", "admin"],
                "write": ["operator", "admin"],
                "control": ["operator", "admin"]
            },
            "camera": {
                "read": ["user", "operator", "admin"],
                "write": ["operator", "admin"],
                "control": ["operator", "admin"]
            },
            "robot": {
                "read": ["user", "operator", "admin"],
                "write": ["operator", "admin"],
                "control": ["operator", "admin"]
            },
            "configuration": {
                "read": ["user", "operator", "admin"],
                "write": ["admin"],
                "delete": ["admin"]
            },
            "users": {
                "read": ["admin"],
                "write": ["admin"],
                "delete": ["admin"]
            }
        }
        
        # Check resource permissions
        if resource in permissions:
            if action in permissions[resource]:
                allowed_levels = permissions[resource][action]
                return user_level in allowed_levels or any(role in allowed_levels for role in user_roles)
        
        # Default deny
        return False


# FastAPI dependency for authentication
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
) -> Dict[str, Any]:
    """FastAPI dependency to get current authenticated user."""
    auth_manager = AuthManager()
    
    try:
        # Verify token
        payload = auth_manager.token_manager.verify_token(credentials.credentials)
        
        # Get user data
        user = {
            "username": payload["sub"],
            "user_id": payload["user_id"],
            "level": payload.get("level", "user"),
            "roles": payload.get("roles", [])
        }
        
        # Store user in request state for audit logging
        if request:
            request.state.user = type('User', (), user)()
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"User authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def require_permission(resource: str, action: str):
    """FastAPI dependency to require specific permission."""
    def permission_checker(user: Dict[str, Any] = Depends(get_current_user)):
        auth_manager = AuthManager()
        
        if not auth_manager.check_permission(user, resource, action):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions for {action} on {resource}"
            )
        
        return user
    
    return permission_checker


async def require_admin(user: Dict[str, Any] = Depends(get_current_user)):
    """FastAPI dependency to require admin level."""
    if user.get("level") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user

