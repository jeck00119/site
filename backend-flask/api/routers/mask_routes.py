from asyncio import sleep

from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket, WebSocketDisconnect
from wsproto.utilities import LocalProtocolError

from api.dependencies.services import get_service_by_type
from api.ws_connection_manager import ConnectionManager
from services.masks.masks_service import MasksService
from src.utils import frame_to_base64

router = APIRouter(
    tags=['mask'],
    prefix='/mask'
)

manager = ConnectionManager()


@router.websocket("/{ws_uid}/crop_roi/ws")
async def websocket_algorithm_img_src(
        ws_uid,
        websocket: WebSocket,
        masks_service: MasksService = Depends(get_service_by_type(MasksService))
):
    await manager.connect(ws_uid, websocket)
    try:
        while True:
            data = await websocket.receive_json()

            try:
                if data["command"] == "set":
                    roi = masks_service.extract_roi(data["image_source_uid"], data["graphics"],
                                                    image_source=data["load_from_image_source"])

                    roi_encoded = frame_to_base64(roi).decode('utf-8')
                    ret = {
                        'roi': roi_encoded
                    }

                    await websocket.send_json(ret)

                if data["command"] == "disconnect":
                    break
            except KeyError:
                pass
            except Exception as e:
                print(f"Exception on cropping: {e}")

            await sleep(0.1)
    except WebSocketDisconnect:
        await manager.disconnect(ws_uid)
    except LocalProtocolError:
        manager.remove_websocket(ws_uid)

    await manager.disconnect(ws_uid)
