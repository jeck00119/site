"""
Security Middleware

Provides comprehensive security middleware for the Industrial Vision Application.
"""

import time
import logging
from typing import Dict, List, Optional, Callable
from collections import defaultdict, deque
from ipaddress import ip_address, ip_network
import asyncio

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config.settings import get_settings
from .audit import AuditLogger


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security middleware providing multiple security features.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
        self.security_config = self.settings.security
        self.logger = logging.getLogger(__name__)
        self.audit_logger = AuditLogger()
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through security checks."""
        start_time = time.time()
        
        try:
            # IP filtering
            if not self._check_ip_access(request):
                await self.audit_logger.log_security_event(
                    "ip_blocked",
                    f"Blocked request from {self._get_client_ip(request)}",
                    request
                )
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Security headers check
            self._validate_request_headers(request)
            
            # Process request
            response = await call_next(request)
            
            # Add security headers to response
            self._add_security_headers(response)
            
            # Log successful request
            processing_time = time.time() - start_time
            if processing_time > 1.0:  # Log slow requests
                await self.audit_logger.log_performance_event(
                    "slow_request",
                    f"Request took {processing_time:.2f}s",
                    request,
                    {"processing_time": processing_time}
                )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Security middleware error: {e}")
            await self.audit_logger.log_security_event(
                "middleware_error",
                f"Security middleware error: {str(e)}",
                request
            )
            raise HTTPException(status_code=500, detail="Internal security error")
    
    def _check_ip_access(self, request: Request) -> bool:
        """Check if client IP is allowed access."""
        client_ip = self._get_client_ip(request)
        
        if not client_ip:
            return True  # Allow if IP cannot be determined
        
        try:
            client_addr = ip_address(client_ip)
            
            # Check blacklist first
            if self.security_config.enable_ip_blacklist:
                for blocked_range in self.security_config.ip_blacklist:
                    if client_addr in ip_network(blocked_range, strict=False):
                        return False
            
            # Check whitelist if enabled
            if self.security_config.enable_ip_whitelist:
                for allowed_range in self.security_config.ip_whitelist:
                    if client_addr in ip_network(allowed_range, strict=False):
                        return True
                return False  # Not in whitelist
            
            return True  # No restrictions or passed checks
            
        except Exception as e:
            self.logger.warning(f"IP access check error for {client_ip}: {e}")
            return True  # Allow on error to avoid blocking legitimate traffic
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Get client IP address from request."""
        # Check for forwarded headers first (for reverse proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return None
    
    def _validate_request_headers(self, request: Request) -> None:
        """Validate request headers for security."""
        # Check for suspicious headers
        suspicious_headers = [
            "X-Forwarded-Host",
            "X-Originating-IP", 
            "X-Remote-IP",
            "X-Cluster-Client-IP"
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                self.logger.warning(f"Suspicious header detected: {header}")
        
        # Validate Content-Type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("Content-Type", "")
            if not content_type and hasattr(request, "body"):
                self.logger.warning("Missing Content-Type header for request with body")
    
    def _add_security_headers(self, response: Response) -> None:
        """Add security headers to response."""
        security_headers = self.security_config.get_security_headers()
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Additional security headers
        if self.security_config.enable_content_type_nosniff:
            response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Remove server information
        if "Server" in response.headers:
            del response.headers["Server"]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with configurable limits and windows.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
        self.security_config = self.settings.security
        self.logger = logging.getLogger(__name__)
        self.audit_logger = AuditLogger()
        
        # Rate limiting storage
        self.request_counts: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, float] = {}
        
        # Cleanup task
        self._cleanup_task = None
        if self.security_config.enable_rate_limiting:
            self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task."""
        async def cleanup():
            while True:
                await asyncio.sleep(60)  # Cleanup every minute
                await self._cleanup_old_requests()
        
        self._cleanup_task = asyncio.create_task(cleanup())
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through rate limiting."""
        if not self.security_config.enable_rate_limiting:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        if not client_ip:
            return await call_next(request)
        
        # Check if IP is currently blocked
        if self._is_ip_blocked(client_ip):
            await self.audit_logger.log_security_event(
                "rate_limit_blocked",
                f"Rate limit exceeded for {client_ip}",
                request
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Check rate limit
        if not self._check_rate_limit(client_ip, request):
            # Block IP temporarily
            self.blocked_ips[client_ip] = time.time() + 300  # Block for 5 minutes
            
            await self.audit_logger.log_security_event(
                "rate_limit_exceeded",
                f"Rate limit exceeded for {client_ip}, IP blocked temporarily",
                request
            )
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. IP temporarily blocked.",
                    "retry_after": 300
                },
                headers={"Retry-After": "300"}
            )
        
        # Record request
        self._record_request(client_ip)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Get client IP address from request."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return None
    
    def _is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked."""
        if ip in self.blocked_ips:
            if time.time() < self.blocked_ips[ip]:
                return True
            else:
                # Unblock expired IP
                del self.blocked_ips[ip]
        return False
    
    def _check_rate_limit(self, ip: str, request: Request) -> bool:
        """Check if request is within rate limits."""
        current_time = time.time()
        window_start = current_time - self.security_config.rate_limit_window
        
        # Get request history for this IP
        requests = self.request_counts[ip]
        
        # Remove old requests outside the window
        while requests and requests[0] < window_start:
            requests.popleft()
        
        # Check if within limits
        request_count = len(requests)
        
        # Apply burst allowance for first few requests
        if request_count < self.security_config.rate_limit_burst:
            return True
        
        # Check regular rate limit
        return request_count < self.security_config.rate_limit_per_minute
    
    def _record_request(self, ip: str) -> None:
        """Record a request for rate limiting."""
        current_time = time.time()
        self.request_counts[ip].append(current_time)
        
        # Limit memory usage by keeping only recent requests
        max_requests = self.security_config.rate_limit_per_minute * 2
        while len(self.request_counts[ip]) > max_requests:
            self.request_counts[ip].popleft()
    
    async def _cleanup_old_requests(self) -> None:
        """Clean up old request records to prevent memory leaks."""
        current_time = time.time()
        window_start = current_time - self.security_config.rate_limit_window
        
        # Clean up request counts
        for ip in list(self.request_counts.keys()):
            requests = self.request_counts[ip]
            
            # Remove old requests
            while requests and requests[0] < window_start:
                requests.popleft()
            
            # Remove empty entries
            if not requests:
                del self.request_counts[ip]
        
        # Clean up expired blocked IPs
        for ip in list(self.blocked_ips.keys()):
            if current_time >= self.blocked_ips[ip]:
                del self.blocked_ips[ip]


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection middleware.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
        self.security_config = self.settings.security
        self.logger = logging.getLogger(__name__)
        self.audit_logger = AuditLogger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through CSRF protection."""
        if not self.security_config.enable_csrf_protection:
            return await call_next(request)
        
        # Skip CSRF check for safe methods
        if request.method in ["GET", "HEAD", "OPTIONS", "TRACE"]:
            return await call_next(request)
        
        # Skip CSRF check for API endpoints with API key
        if self._has_valid_api_key(request):
            return await call_next(request)
        
        # Check CSRF token
        if not self._validate_csrf_token(request):
            await self.audit_logger.log_security_event(
                "csrf_violation",
                f"CSRF token validation failed for {request.url}",
                request
            )
            raise HTTPException(status_code=403, detail="CSRF token validation failed")
        
        return await call_next(request)
    
    def _has_valid_api_key(self, request: Request) -> bool:
        """Check if request has valid API key."""
        if not self.security_config.api_key_enabled:
            return False
        
        api_key = request.headers.get(self.security_config.api_key_header)
        return api_key in self.security_config.api_keys
    
    def _validate_csrf_token(self, request: Request) -> bool:
        """Validate CSRF token."""
        # Get token from header or form data
        csrf_token = request.headers.get("X-CSRF-Token")
        
        if not csrf_token:
            # Try to get from form data (for form submissions)
            # This would require parsing the request body
            return False
        
        # Validate token format and signature
        # Implementation would depend on token generation strategy
        return len(csrf_token) >= 32  # Basic validation
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session."""
        import hmac
        import hashlib
        import secrets
        
        # Generate random component
        random_part = secrets.token_urlsafe(16)
        
        # Create HMAC signature
        message = f"{session_id}:{random_part}"
        signature = hmac.new(
            self.security_config.csrf_secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{random_part}:{signature}"

