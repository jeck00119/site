import asyncio
import wsproto.utilities
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from src.metaclasses.singleton import Singleton


class Socket:
    def __init__(self, websocket: WebSocket, running: bool):
        self.websocket = websocket
        self.running = running

    async def disconnect(self):
        from starlette.websockets import WebSocketState
        print(self.websocket.client_state)
        try:
            # Only close if the WebSocket is still connected
            if self.websocket.client_state == WebSocketState.CONNECTED:
                await self.websocket.close()
        except (wsproto.utilities.LocalProtocolError, RuntimeError) as e:
            # WebSocket already closed or in process of closing
            pass
        finally:
            self.running = False

    def get_websocket(self):
        return self.websocket

    def status(self):
        return self.running

    def set_closed(self):
        self.running = False


class ConnectionManager(metaclass=Singleton):
    def __init__(self):
        self.active_connections: dict[str, Socket] = {}

    @staticmethod
    async def safe_sleep_with_cancellation(duration: float):
        """
        Centralized sleep method that handles cancellation gracefully.
        Use this instead of asyncio.sleep() in WebSocket loops.
        """
        try:
            await asyncio.sleep(duration)
            return True  # Normal completion
        except asyncio.CancelledError:
            return False  # Cancelled, should break loop

    @staticmethod
    def handle_websocket_exceptions(func):
        """
        Decorator for centralized WebSocket exception handling.
        Handles common WebSocket exceptions with consistent behavior.
        """
        def wrapper(*args, **kwargs):
            async def async_wrapper():
                uid = args[0] if args else kwargs.get('uid', 'unknown')
                manager = ConnectionManager()
                try:
                    return await func(*args, **kwargs)
                except WebSocketDisconnect:
                    await manager.disconnect(uid)
                except asyncio.CancelledError:
                    # Handle cancellation during shutdown
                    manager.remove_websocket(uid)
                    raise  # Re-raise to stop execution
                except Exception as e:
                    print(f"WebSocket error for {uid}: {e}")
                    manager.remove_websocket(uid)
            return async_wrapper()
        return wrapper

    async def connect(self, uid, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[uid] = Socket(websocket, True)

    async def _disconnect_all(self):
        # Create a copy of keys to avoid iteration error during shutdown
        connection_ids = list(self.active_connections.keys())
        for uid in connection_ids:
            await self.disconnect(uid)

    async def connection_closed(self, uid):
        try:
            await self.active_connections[uid].disconnect()
            print(f"SOCKET DISCONNECTED: {uid}")
        except KeyError:
            print(f"ERROR ON SOCKET DISCONNECT: {uid}")
            pass

    def is_closed(self, uid):
        return not self.active_connections[uid].status()

    async def disconnect(self, uid):
        from starlette.websockets import WebSocketState
        # Check if the socket still exists in active connections
        if uid not in self.active_connections:
            print(f"SOCKET ALREADY REMOVED: {uid}")
            return
            
        socket = self.active_connections[uid].get_websocket()
        try:
            # Only close if the WebSocket is still connected
            if socket.client_state == WebSocketState.CONNECTED:
                await socket.close()
                print(f"CLOSING SOCKET: {uid}")
            else:
                print(f"SOCKET ALREADY CLOSED: {uid}")
        except Exception:
            pass

        self.remove_websocket(uid)

    def remove_websocket(self, uid):
        if uid in self.active_connections:
            print(f"REMOVING SOCKET: {uid} FROM ACTIVE SOCKETS LIST")
            del self.active_connections[uid]
        else:
            print(f"SOCKET {uid} NOT IN ACTIVE CONNECTIONS LIST")
