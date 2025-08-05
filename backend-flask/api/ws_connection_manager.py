import wsproto.utilities
from starlette.websockets import WebSocket

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

    async def connect(self, uid, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[uid] = Socket(websocket, True)

    async def _disconnect_all(self):
        for uid in self.active_connections.keys():
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
        print(f"REMOVING SOCKET: {uid} FROM ACTIVE SOCKETS LIST")
        del self.active_connections[uid]
