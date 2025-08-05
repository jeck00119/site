"""
Centralized Error Handling System

Provides consistent error handling decorators and utilities for all API routes.
Eliminates duplicate error handling code and ensures consistent error messages.
"""

import functools
import logging
from typing import Callable, Dict, Any, Optional, Type
from fastapi import HTTPException, status
from starlette.responses import JSONResponse

from repo.repository_exceptions import UidNotFound, UidNotUnique, NoConfigurationChosen, UserNotFound
from services.services_exceptions import NoLiveAlgSet, NoLiveFrameSet

logger = logging.getLogger(__name__)

# Standard error mappings
ERROR_MAPPINGS = {
    UidNotFound: {
        'status_code': status.HTTP_404_NOT_FOUND,
        'message_template': '{entity_type} with UID {entity_id} not found'
    },
    UidNotUnique: {
        'status_code': status.HTTP_409_CONFLICT,
        'message_template': '{entity_type} with UID {entity_id} already exists'
    },
    NoConfigurationChosen: {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'message_template': 'No configuration selected. Please load a configuration first'
    },
    UserNotFound: {
        'status_code': status.HTTP_404_NOT_FOUND,
        'message_template': 'User {entity_id} not found'
    },
    NoLiveAlgSet: {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'message_template': 'No live algorithm set. Please configure an algorithm first'
    },
    NoLiveFrameSet: {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'message_template': 'No live frame set. Please capture or load a frame first'
    }
}

def create_error_response(
    operation: str,
    entity_type: str = "Entity",
    entity_id: str = None,
    exception: Exception = None,
    status_code: int = None,
    custom_message: str = None
) -> HTTPException:
    """
    Create a standardized error response.
    
    Args:
        operation: The operation that failed (e.g., "create", "update", "delete")
        entity_type: Type of entity (e.g., "CNC", "Configuration", "Camera")
        entity_id: ID of the entity (optional)
        exception: The original exception
        status_code: Custom status code (optional)
        custom_message: Custom error message (optional)
    
    Returns:
        HTTPException with standardized error message
    """
    if custom_message:
        detail = custom_message
    elif exception and type(exception) in ERROR_MAPPINGS:
        mapping = ERROR_MAPPINGS[type(exception)]
        detail = mapping['message_template'].format(
            entity_type=entity_type,
            entity_id=entity_id or "unknown"
        )
        if not status_code:
            status_code = mapping['status_code']
    else:
        detail = f"Failed to {operation} {entity_type.lower()}"
        if entity_id:
            detail += f" {entity_id}"
        if exception:
            detail += f": {str(exception)}"
    
    # Default status code
    if not status_code:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # Log the error for debugging
    logger.error(f"API Error [{status_code}]: {detail}")
    if exception:
        logger.exception(f"Exception details for {operation} {entity_type}: {exception}")
    
    return HTTPException(status_code=status_code, detail=detail)

def handle_route_errors(
    operation: str, 
    entity_type: str = "Entity",
    entity_id_param: str = None,
    success_message: str = None,
    success_status: int = status.HTTP_200_OK
):
    """
    Decorator for consistent route error handling.
    
    Args:
        operation: The operation being performed
        entity_type: Type of entity being operated on
        entity_id_param: Name of the parameter containing entity ID
        success_message: Custom success message
        success_status: Success status code
    
    Usage:
        @handle_route_errors("create", "CNC", success_status=201)
        async def create_cnc(cnc_model: CncModel, ...):
            # route logic here
            return result
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                
                # If result is already a Response, return it
                if hasattr(result, 'status_code'):
                    return result
                
                # Create success response
                if success_message:
                    entity_id = kwargs.get(entity_id_param, "")
                    message = success_message.format(
                        entity_type=entity_type,
                        entity_id=entity_id,
                        operation=operation
                    )
                    return JSONResponse(
                        status_code=success_status,
                        content={"status": "success", "message": message}
                    )
                
                return result
                
            except HTTPException:
                # Re-raise HTTPExceptions (already handled)
                raise
            except Exception as e:
                entity_id = kwargs.get(entity_id_param) if entity_id_param else None
                raise create_error_response(
                    operation=operation,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    exception=e
                )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # If result is already a Response, return it
                if hasattr(result, 'status_code'):
                    return result
                
                # Create success response
                if success_message:
                    entity_id = kwargs.get(entity_id_param, "")
                    message = success_message.format(
                        entity_type=entity_type,
                        entity_id=entity_id,
                        operation=operation
                    )
                    return JSONResponse(
                        status_code=success_status,
                        content={"status": "success", "message": message}
                    )
                
                return result
                
            except HTTPException:
                # Re-raise HTTPExceptions (already handled)
                raise
            except Exception as e:
                entity_id = kwargs.get(entity_id_param) if entity_id_param else None
                raise create_error_response(
                    operation=operation,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    exception=e
                )
        
        # Return appropriate wrapper based on function type
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

def handle_cnc_operation_errors(operation: str, cnc_service, cnc_uid: str):
    """
    Specialized error handler for CNC operations that checks connection status.
    
    Args:
        operation: The CNC operation being performed
        cnc_service: CNC service instance
        cnc_uid: CNC UID
    
    Raises:
        HTTPException: If CNC is not connected or operation fails
    """
    cnc_info = cnc_service.get_cnc_info(cnc_uid)
    
    if not cnc_info.get('exists', False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CNC {cnc_uid} not found"
        )
    
    if cnc_info.get('is_mock', False):
        connection_error = cnc_info.get('connection_error', 'Unknown connection error')
        cnc_name = cnc_info.get('name', cnc_uid)
        cnc_port = cnc_info.get('port', 'Unknown')
        cnc_type = cnc_info.get('type', 'Unknown')
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CNC '{cnc_name}' ({cnc_type}) is not connected to port {cnc_port}. "
                   f"Cannot execute {operation} command. Connection error: {connection_error}"
        )

def validate_authentication(user: dict, operation: str = "perform this operation"):
    """
    Validate user authentication.
    
    Args:
        user: User object from authentication
        operation: Description of the operation being performed
    
    Raises:
        HTTPException: If authentication fails
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication required to {operation}"
        )

# Import asyncio at the end to avoid circular imports
import asyncio