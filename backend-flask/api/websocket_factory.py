"""
WebSocket Route Factory

Eliminates duplicate WebSocket endpoint implementations across 10+ route files.
Provides a centralized factory for creating WebSocket routes with consistent behavior.
"""

import asyncio
import logging
from typing import Callable, Optional, Dict, Any
from fastapi import APIRouter, WebSocket, Depends
from starlette.websockets import WebSocketDisconnect
from wsproto.utilities import LocalProtocolError

from api.ws_connection_manager import ConnectionManager
from api.dependencies.services import get_service_by_type

logger = logging.getLogger(__name__)


class WebSocketRouteFactory:
    """
    Factory for creating WebSocket routes with consistent implementation.
    Eliminates duplicate WebSocket code across multiple route files.
    """
    
    def __init__(self, connection_manager: Optional[ConnectionManager] = None):
        """
        Initialize WebSocket route factory.
        
        Args:
            connection_manager: Optional connection manager instance
        """
        self.manager = connection_manager or ConnectionManager()
    
    def create_websocket_route(
        self,
        router: APIRouter,
        entity_type: str,
        service_class: type,
        process_method: str = "process",
        send_method: str = "send_json",
        path_suffix: str = None,
        additional_dependencies: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Create a WebSocket route for an entity type.
        
        Args:
            router: FastAPI router to add the route to
            entity_type: Type of entity (e.g., 'camera', 'cnc', 'robot')
            service_class: Service class to use for processing
            process_method: Method name to call on service for processing
            send_method: Method to use for sending data ('send_json' or 'send_bytes')
            path_suffix: Optional path suffix (default: /ws/{entity_type}_uid)
            additional_dependencies: Additional FastAPI dependencies
        """
        
        # Build the path
        uid_param = f"{entity_type}_uid"
        path = path_suffix or f"/ws/{{{uid_param}}}"
        
        # Create the WebSocket endpoint
        @router.websocket(path)
        async def websocket_endpoint(
            websocket: WebSocket,
            **kwargs
        ):
            """Generic WebSocket endpoint handler."""
            entity_uid = kwargs.get(uid_param)
            service = None
            
            try:
                # Connect WebSocket
                await self.manager.connect(websocket, entity_uid)
                logger.info(f"WebSocket connected for {entity_type} {entity_uid}")
                
                # Get service instance
                service = get_service_by_type(service_class)()
                
                # Main WebSocket loop
                while True:
                    try:
                        # Check if service has the process method
                        if hasattr(service, process_method):
                            # Process entity
                            result = await self._process_entity(
                                service, process_method, entity_uid
                            )
                            
                            # Send result
                            await self._send_result(
                                websocket, result, send_method
                            )
                        else:
                            # Just keep connection alive
                            await asyncio.sleep(0.1)
                        
                        # Receive any client messages (for bidirectional communication)
                        # Non-blocking check for client messages
                        try:
                            client_message = await asyncio.wait_for(
                                websocket.receive_json(), 
                                timeout=0.01
                            )
                            await self._handle_client_message(
                                service, entity_type, entity_uid, client_message
                            )
                        except asyncio.TimeoutError:
                            pass  # No message from client
                            
                    except WebSocketDisconnect:
                        break
                    except Exception as e:
                        logger.error(f"Error in WebSocket loop for {entity_type} {entity_uid}: {e}")
                        await asyncio.sleep(0.1)  # Prevent tight error loop
                        
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for {entity_type} {entity_uid}")
            except LocalProtocolError as e:
                logger.error(f"WebSocket protocol error for {entity_type} {entity_uid}: {e}")
            except Exception as e:
                logger.error(f"WebSocket error for {entity_type} {entity_uid}: {e}")
            finally:
                # Clean up
                self.manager.remove_websocket(websocket, entity_uid)
                logger.info(f"WebSocket cleaned up for {entity_type} {entity_uid}")
        
        # Store the endpoint on the router for reference
        setattr(router, f"{entity_type}_websocket", websocket_endpoint)
    
    async def _process_entity(
        self, 
        service: Any, 
        method_name: str, 
        entity_uid: str
    ) -> Any:
        """
        Process entity using service method.
        
        Args:
            service: Service instance
            method_name: Method to call on service
            entity_uid: Entity UID
            
        Returns:
            Processing result
        """
        method = getattr(service, method_name)
        
        # Check if method is async
        if asyncio.iscoroutinefunction(method):
            return await method(entity_uid)
        else:
            # Run sync method in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, method, entity_uid)
    
    async def _send_result(
        self, 
        websocket: WebSocket, 
        result: Any, 
        send_method: str
    ) -> None:
        """
        Send result through WebSocket.
        
        Args:
            websocket: WebSocket connection
            result: Result to send
            send_method: Method to use for sending
        """
        if result is not None:
            if send_method == "send_json":
                await websocket.send_json(result)
            elif send_method == "send_bytes":
                await websocket.send_bytes(result)
            else:
                # Default to JSON
                await websocket.send_json(result)
    
    async def _handle_client_message(
        self,
        service: Any,
        entity_type: str,
        entity_uid: str,
        message: Dict[str, Any]
    ) -> None:
        """
        Handle messages from client.
        
        Args:
            service: Service instance
            entity_type: Type of entity
            entity_uid: Entity UID
            message: Message from client
        """
        # Check if service has a message handler
        handler_method = f"handle_{entity_type}_message"
        if hasattr(service, handler_method):
            handler = getattr(service, handler_method)
            if asyncio.iscoroutinefunction(handler):
                await handler(entity_uid, message)
            else:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, handler, entity_uid, message)
        else:
            logger.debug(f"No message handler for {entity_type}: {message}")
    
    def create_streaming_websocket(
        self,
        router: APIRouter,
        entity_type: str,
        service_class: type,
        stream_method: str,
        frame_processor: Optional[Callable] = None
    ) -> None:
        """
        Create a streaming WebSocket for continuous data (e.g., camera frames).
        
        Args:
            router: FastAPI router
            entity_type: Type of entity
            service_class: Service class
            stream_method: Method that yields/returns frames
            frame_processor: Optional function to process frames before sending
        """
        
        uid_param = f"{entity_type}_uid"
        path = f"/stream/{{{uid_param}}}"
        
        @router.websocket(path)
        async def streaming_websocket(
            websocket: WebSocket,
            **kwargs
        ):
            """Streaming WebSocket endpoint."""
            entity_uid = kwargs.get(uid_param)
            
            try:
                await self.manager.connect(websocket, entity_uid)
                service = get_service_by_type(service_class)()
                
                # Get stream method
                stream = getattr(service, stream_method)
                
                # Stream data
                if asyncio.iscoroutinefunction(stream):
                    async for frame in stream(entity_uid):
                        if frame_processor:
                            frame = frame_processor(frame)
                        await websocket.send_bytes(frame)
                else:
                    # Handle sync generator
                    loop = asyncio.get_event_loop()
                    for frame in await loop.run_in_executor(None, stream, entity_uid):
                        if frame_processor:
                            frame = frame_processor(frame)
                        await websocket.send_bytes(frame)
                        
            except WebSocketDisconnect:
                logger.info(f"Stream disconnected for {entity_type} {entity_uid}")
            except Exception as e:
                logger.error(f"Stream error for {entity_type} {entity_uid}: {e}")
            finally:
                self.manager.remove_websocket(websocket, entity_uid)
        
        setattr(router, f"{entity_type}_stream", streaming_websocket)


# Global factory instance
websocket_factory = WebSocketRouteFactory()


def setup_standard_websocket_routes(router: APIRouter, entity_type: str, service_class: type):
    """
    Convenience function to set up standard WebSocket routes.
    
    Args:
        router: FastAPI router
        entity_type: Entity type
        service_class: Service class
    """
    websocket_factory.create_websocket_route(
        router=router,
        entity_type=entity_type,
        service_class=service_class
    )