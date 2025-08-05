"""
Audit Logging System

Provides comprehensive audit logging for security and operational events.
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import Request
from config.settings import get_settings
from src.metaclasses.singleton import Singleton


class AuditLogger(metaclass=Singleton):
    """
    Comprehensive audit logging system for security and operational events.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.security_config = self.settings.security
        self.logging_config = self.settings.logging
        self.logger = logging.getLogger("audit")
        
        # Setup audit log file
        self._setup_audit_logging()
        
        # Event queue for async processing
        self._event_queue = asyncio.Queue()
        self._processing_task = None
        
        if self.security_config.enable_audit_logging:
            self._start_processing_task()
    
    def _setup_audit_logging(self):
        """Setup audit log file handler."""
        if not self.security_config.enable_audit_logging:
            return
        
        # Create audit log directory
        audit_log_path = Path(self.logging_config.log_directory) / self.logging_config.audit_log_filename
        audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup file handler for audit logs
        handler = logging.FileHandler(audit_log_path)
        handler.setLevel(logging.INFO)
        
        # JSON formatter for structured logging
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _start_processing_task(self):
        """Start background task for processing audit events."""
        async def process_events():
            while True:
                try:
                    event = await self._event_queue.get()
                    await self._write_audit_event(event)
                    self._event_queue.task_done()
                except Exception as e:
                    logging.error(f"Error processing audit event: {e}")
        
        self._processing_task = asyncio.create_task(process_events())
    
    async def log_security_event(
        self,
        event_type: str,
        description: str,
        request: Optional[Request] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log a security-related event."""
        event = self._create_event(
            category="security",
            event_type=event_type,
            description=description,
            request=request,
            additional_data=additional_data
        )
        
        if self.security_config.enable_audit_logging:
            await self._queue_event(event)
    
    async def log_authentication_event(
        self,
        event_type: str,
        username: str,
        success: bool,
        request: Optional[Request] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log an authentication-related event."""
        event_data = {
            "username": username,
            "success": success,
            **(additional_data or {})
        }
        
        event = self._create_event(
            category="authentication",
            event_type=event_type,
            description=f"Authentication {event_type} for user {username}",
            request=request,
            additional_data=event_data
        )
        
        if self.security_config.enable_audit_logging:
            await self._queue_event(event)
    
    async def log_authorization_event(
        self,
        event_type: str,
        username: str,
        resource: str,
        action: str,
        success: bool,
        request: Optional[Request] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log an authorization-related event."""
        event_data = {
            "username": username,
            "resource": resource,
            "action": action,
            "success": success,
            **(additional_data or {})
        }
        
        event = self._create_event(
            category="authorization",
            event_type=event_type,
            description=f"Authorization {event_type} for user {username} on {resource}",
            request=request,
            additional_data=event_data
        )
        
        if self.security_config.enable_audit_logging:
            await self._queue_event(event)
    
    async def log_configuration_event(
        self,
        event_type: str,
        username: str,
        configuration_name: str,
        changes: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """Log a configuration change event."""
        event_data = {
            "username": username,
            "configuration_name": configuration_name,
            "changes": changes
        }
        
        event = self._create_event(
            category="configuration",
            event_type=event_type,
            description=f"Configuration {event_type} by {username}",
            request=request,
            additional_data=event_data
        )
        
        if self.security_config.enable_audit_logging:
            await self._queue_event(event)
    
    async def log_data_access_event(
        self,
        event_type: str,
        username: str,
        data_type: str,
        data_id: str,
        action: str,
        request: Optional[Request] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log a data access event."""
        event_data = {
            "username": username,
            "data_type": data_type,
            "data_id": data_id,
            "action": action,
            **(additional_data or {})
        }
        
        event = self._create_event(
            category="data_access",
            event_type=event_type,
            description=f"Data access {action} on {data_type}:{data_id} by {username}",
            request=request,
            additional_data=event_data
        )
        
        if self.security_config.enable_audit_logging:
            await self._queue_event(event)
    
    async def log_system_event(
        self,
        event_type: str,
        description: str,
        component: str,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log a system-related event."""
        event_data = {
            "component": component,
            **(additional_data or {})
        }
        
        event = self._create_event(
            category="system",
            event_type=event_type,
            description=description,
            additional_data=event_data
        )
        
        if self.security_config.enable_audit_logging:
            await self._queue_event(event)
    
    async def log_performance_event(
        self,
        event_type: str,
        description: str,
        request: Optional[Request] = None,
        metrics: Optional[Dict[str, Any]] = None
    ):
        """Log a performance-related event."""
        event = self._create_event(
            category="performance",
            event_type=event_type,
            description=description,
            request=request,
            additional_data=metrics
        )
        
        if self.logging_config.enable_performance_logging:
            await self._queue_event(event)
    
    def _create_event(
        self,
        category: str,
        event_type: str,
        description: str,
        request: Optional[Request] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a structured audit event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "category": category,
            "event_type": event_type,
            "description": description,
            "severity": self._get_event_severity(category, event_type),
        }
        
        # Add request information if available
        if request:
            event["request"] = self._extract_request_info(request)
        
        # Add additional data
        if additional_data:
            event["data"] = self._sanitize_data(additional_data)
        
        return event
    
    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Extract relevant information from request."""
        info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "user_agent": request.headers.get("User-Agent"),
            "referer": request.headers.get("Referer"),
        }
        
        # Add client IP
        client_ip = self._get_client_ip(request)
        if client_ip:
            info["client_ip"] = client_ip
        
        # Add authentication info if available
        if hasattr(request.state, "user"):
            info["user"] = {
                "username": getattr(request.state.user, "username", None),
                "user_id": getattr(request.state.user, "id", None),
                "roles": getattr(request.state.user, "roles", [])
            }
        
        return info
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Get client IP from request."""
        # Check forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Direct connection
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return None
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive data for logging."""
        if not self.logging_config.mask_sensitive_data:
            return data
        
        sanitized = {}
        for key, value in data.items():
            if self.logging_config.should_mask_field(key):
                if isinstance(value, str):
                    sanitized[key] = self.logging_config.mask_sensitive_value(value)
                else:
                    sanitized[key] = "***MASKED***"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _get_event_severity(self, category: str, event_type: str) -> str:
        """Determine event severity based on category and type."""
        high_severity_events = [
            "authentication_failure",
            "authorization_failure", 
            "security_violation",
            "data_breach",
            "system_compromise",
            "privilege_escalation"
        ]
        
        medium_severity_events = [
            "configuration_change",
            "user_creation",
            "permission_change",
            "rate_limit_exceeded"
        ]
        
        if event_type in high_severity_events:
            return "HIGH"
        elif event_type in medium_severity_events:
            return "MEDIUM"
        else:
            return "LOW"
    
    async def _queue_event(self, event: Dict[str, Any]):
        """Queue event for async processing."""
        try:
            await self._event_queue.put(event)
        except Exception as e:
            logging.error(f"Failed to queue audit event: {e}")
            # Fallback to synchronous logging
            await self._write_audit_event(event)
    
    async def _write_audit_event(self, event: Dict[str, Any]):
        """Write audit event to log."""
        try:
            # Convert to JSON string
            event_json = json.dumps(event, default=str, separators=(',', ':'))
            
            # Log the event
            self.logger.info(event_json)
            
        except Exception as e:
            logging.error(f"Failed to write audit event: {e}")
    
    async def search_events(
        self,
        category: Optional[str] = None,
        event_type: Optional[str] = None,
        username: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search audit events with filters."""
        # This is a basic implementation
        # In production, you might want to use a proper search engine or database
        
        events = []
        audit_log_path = Path(self.logging_config.log_directory) / self.logging_config.audit_log_filename
        
        if not audit_log_path.exists():
            return events
        
        try:
            with open(audit_log_path, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        
                        # Apply filters
                        if category and event.get("category") != category:
                            continue
                        
                        if event_type and event.get("event_type") != event_type:
                            continue
                        
                        if username:
                            event_username = event.get("request", {}).get("user", {}).get("username")
                            if event_username != username:
                                continue
                        
                        if start_time:
                            event_time = datetime.fromisoformat(event["timestamp"])
                            if event_time < start_time:
                                continue
                        
                        if end_time:
                            event_time = datetime.fromisoformat(event["timestamp"])
                            if event_time > end_time:
                                continue
                        
                        events.append(event)
                        
                        if len(events) >= limit:
                            break
                            
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            logging.error(f"Error searching audit events: {e}")
        
        return events
    
    async def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get security event summary for the specified time period."""
        end_time = datetime.utcnow()
        start_time = end_time.replace(hour=end_time.hour - hours)
        
        events = await self.search_events(
            category="security",
            start_time=start_time,
            end_time=end_time,
            limit=1000
        )
        
        summary = {
            "total_events": len(events),
            "high_severity": 0,
            "medium_severity": 0,
            "low_severity": 0,
            "event_types": {},
            "top_ips": {},
            "time_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            }
        }
        
        for event in events:
            # Count by severity
            severity = event.get("severity", "LOW")
            if severity == "HIGH":
                summary["high_severity"] += 1
            elif severity == "MEDIUM":
                summary["medium_severity"] += 1
            else:
                summary["low_severity"] += 1
            
            # Count by event type
            event_type = event.get("event_type", "unknown")
            summary["event_types"][event_type] = summary["event_types"].get(event_type, 0) + 1
            
            # Count by IP
            client_ip = event.get("request", {}).get("client_ip")
            if client_ip:
                summary["top_ips"][client_ip] = summary["top_ips"].get(client_ip, 0) + 1
        
        return summary

