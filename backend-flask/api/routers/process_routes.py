import logging
import os
import traceback
from asyncio import sleep

from fastapi import APIRouter, HTTPException, Depends, Body
from starlette import status
from starlette.responses import FileResponse, JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from wsproto.utilities import LocalProtocolError

from api.dependencies.services import get_service_by_type
from api.error_handlers import handle_route_errors, create_error_response
from api.ws_connection_manager import ConnectionManager
from services.processing.process_service import ProcessService

router = APIRouter(
    tags=['processing'],
    prefix='/processing'
)


@router.get('/start_process')
@handle_route_errors("start", "Process")
async def start_process(
        offline: bool,
        process_service: ProcessService = Depends(get_service_by_type(ProcessService))
):
    # Configure logging to write to a file
    if not os.path.exists('./process_log/yolo'):
        os.makedirs('./process_log/yolo')
    logging.basicConfig(filename='./process_log/yolo/exceptions.log', level=logging.ERROR,
                        format='%(asctime)s - %(levelname)s: %(message)s')

    try:
        await process_service.start_process(offline=offline)
        return JSONResponse(status_code=status.HTTP_200_OK, content='')
    except Exception as e:
        # Capture the full stack trace
        stack_trace = traceback.format_exc()
        logging.error(f"Exception: {e}")
        logging.error("Full stack trace:\n%s", stack_trace)
        process_service.stop_process()
        # Let the decorator handle the error response
        raise e


@router.get('/stop_process')
@handle_route_errors("stop", "Process")
async def stop_process(
        process_service: ProcessService = Depends(get_service_by_type(ProcessService))
):
    process_service.stop_process()
    return JSONResponse(status_code=status.HTTP_200_OK, content='')


@router.get('/process_state')
@handle_route_errors("retrieve", "Process state")
async def get_process_state(
        process_service: ProcessService = Depends(get_service_by_type(ProcessService)),
):
    pass
    # return process_service.state


@router.get('/capability/state')
@handle_route_errors("retrieve", "Process capability state")
async def get_capability_state(
        process_service: ProcessService = Depends(get_service_by_type(ProcessService)),
):
    return process_service.capability_mode_state


@router.put('/capability/state')
@handle_route_errors("update", "Process capability state")
async def set_capability_state(
        state: bool,
        number:int,
        process_service: ProcessService = Depends(get_service_by_type(ProcessService)),
):
    process_service.capability_mode_state = state
    return JSONResponse(status_code=status.HTTP_200_OK, content='')


@router.get('/offset/state')
@handle_route_errors("retrieve", "Process offset state")
async def get_offset_state(
        process_service: ProcessService = Depends(get_service_by_type(ProcessService)),
):
    return process_service.offset_mode_state


@router.put('/offset/state')
@handle_route_errors("update", "Process offset state")
async def set_offset_state(
        state: bool,
        process_service: ProcessService = Depends(get_service_by_type(ProcessService)),
):
    process_service.offset_mode_state = state
    return JSONResponse(status_code=status.HTTP_200_OK, content='')


@router.get('/capability_report')
@handle_route_errors("retrieve", "Process capability report")
async def capability_report():
    headers = {'Content-Disposition': 'attachment; filename="capability_report.xlsx"'}
    report_path = os.path.join(os.getcwd(), "reports", "capability_report.xlsx")
    
    # Ensure the reports directory exists
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    # Check if file exists, create a basic one if not
    if not os.path.exists(report_path):
        # You should implement actual report generation here
        raise create_error_response(
            operation="retrieve",
            entity_type="Process capability report",
            status_code=status.HTTP_404_NOT_FOUND,
            custom_message="Capability report not found. Please generate report first."
        )
    
    return FileResponse(report_path, headers=headers)


@router.post('/save_image_flag')
@handle_route_errors("update", "Process save image flag")
async def set_save_image_flag(
    value: bool = Body(...),
    process_service: ProcessService = Depends(get_service_by_type(ProcessService))
):
    process_service.set_save_image_flag(value)
    return JSONResponse(status_code=status.HTTP_200_OK, content='')


manager = ConnectionManager()


@router.websocket("/{process_uid}/process")
async def websocket_endpoint(
        process_uid,
        websocket: WebSocket,
        process_service: ProcessService = Depends(get_service_by_type(ProcessService))
):
    await manager.connect(process_uid, websocket)
    try:
        while True:
            if manager.is_closed(process_uid):
                break

            msg = process_service.read_process_status_to_ws_deque()

            if msg:
                await websocket.send_json(msg)

            await sleep(0.1)

        await manager.disconnect(process_uid)
    except WebSocketDisconnect:
        await manager.disconnect(process_uid)
    except LocalProtocolError:
        pass
    except RuntimeError as e:
        pass


@router.post("/{process_uid}/ws/close")
@handle_route_errors("close", "Process WebSocket", "process_uid")
async def close_ws(process_uid):
    await manager.connection_closed(process_uid)
    return JSONResponse(status_code=status.HTTP_200_OK, content='')
