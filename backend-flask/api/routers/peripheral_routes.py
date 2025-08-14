import os.path
import subprocess
from asyncio import sleep
from typing import Dict, Any

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from wsproto.utilities import LocalProtocolError

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response
from api.route_utils import RouteHelper
from api.ws_connection_manager import ConnectionManager
from services.port_manager.port_manager import UnifiedUSBManager
from src.platform_utils import CommandExecutor

router = APIRouter(
    tags=['peripheral'],
    prefix='/peripheral'
)

manager = ConnectionManager()


@router.websocket("/{ws_uid}/cognex_status/ws")
async def websocket_get_cognex_status(
        ws_uid: str,
        websocket: WebSocket,
        port_manager: UnifiedUSBManager = Depends(get_service_by_type(UnifiedUSBManager))
):
    await manager.connect(ws_uid, websocket)

    try:
        while True:
            if manager.is_closed(ws_uid):
                break

            # Use centralized USB manager for cross-platform Cognex detection
            cognex_devices = await port_manager.get_available_ports_by_type('dmc_readers')
            ret = {
                'status': len(cognex_devices) > 0,
                'devices': cognex_devices
            }

            await websocket.send_json(ret)
            await sleep(1)

        await manager.disconnect(ws_uid)
    except WebSocketDisconnect:
        await manager.disconnect(ws_uid)
    except LocalProtocolError:
        manager.remove_websocket(ws_uid)
    except RuntimeError:
        manager.remove_websocket(ws_uid)


@router.websocket("/{ws_uid}/camera_status/ws")
async def websocket_get_camera_status(
        ws_uid: str, 
        websocket: WebSocket,
        port_manager: UnifiedUSBManager = Depends(get_service_by_type(UnifiedUSBManager))
):
    await manager.connect(ws_uid, websocket)

    try:
        while True:
            if manager.is_closed(ws_uid):
                break

            # Use centralized USB manager for cross-platform camera detection
            cameras = await port_manager.get_available_ports_by_type('cameras')
            ret = {
                'status': len(cameras) > 0,
                'cameras': cameras
            }

            await websocket.send_json(ret)
            await sleep(1)

        await manager.disconnect(ws_uid)
    except WebSocketDisconnect:
        await manager.disconnect(ws_uid)
    except LocalProtocolError:
        manager.remove_websocket(ws_uid)
    except RuntimeError:
        manager.remove_websocket(ws_uid)


@router.post("/{ws_uid}/ws/close")
async def close_ws(ws_uid: str) -> JSONResponse:
    try:
        await manager.connection_closed(ws_uid)
        return RouteHelper.create_success_response("")
    except Exception as e:
        raise create_error_response("close_ws", "Peripheral", exception=e)
