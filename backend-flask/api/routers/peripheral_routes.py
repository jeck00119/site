import os.path
import subprocess
from asyncio import sleep
from typing import Dict, Any

from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from wsproto.utilities import LocalProtocolError

from api.error_handlers import create_error_response
from api.route_utils import RouteHelper
from api.ws_connection_manager import ConnectionManager
from src.platform_utils import is_windows, is_linux, CommandExecutor

router = APIRouter(
    tags=['peripheral'],
    prefix='/peripheral'
)

manager = ConnectionManager()


@router.websocket("/{ws_uid}/cognex_status/ws")
async def websocket_get_cognex_status(
        ws_uid: str,
        websocket: WebSocket
):
    await manager.connect(ws_uid, websocket)

    try:
        while True:
            if manager.is_closed(ws_uid):
                break

            ret = {}

            if is_windows():
                # Windows Cognex device detection
                ret['status'] = False
                # TODO: Implement Windows-specific Cognex device detection
            elif is_linux():
                # Linux Cognex device detection using lsusb
                usb_devices = CommandExecutor.check_usb_devices()
                ret['status'] = any("1447:8022" in device["id"] for device in usb_devices)
            else:
                ret['status'] = False

            # if os.path.isdir("/dev/serial/by-id"):
            #     ret['status'] = True
            # else:
            #     ret['status'] = False

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
async def websocket_get_camera_status(ws_uid: str, websocket: WebSocket):
    await manager.connect(ws_uid, websocket)

    try:
        while True:
            if manager.is_closed(ws_uid):
                break

            ret = {}
            
            # Use cross-platform camera detection
            cameras = CommandExecutor.check_camera_devices()
            ret['status'] = len(cameras) > 0
            ret['cameras'] = cameras

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
