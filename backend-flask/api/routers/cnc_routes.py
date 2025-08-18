import asyncio
from asyncio import sleep

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from wsproto.utilities import LocalProtocolError

from api.dependencies.services import get_service_by_type
from api.ws_connection_manager import ConnectionManager
from api.error_handlers import create_error_response, handle_cnc_operation_errors, validate_authentication
from api.route_utils import RouteHelper, require_authentication
from repo.repositories import CncRepository, LocationRepository
from repo.repository_exceptions import UidNotFound, UidNotUnique
from services.authorization.authorization import get_current_user
from services.cnc.cnc_models import CncModel, LocationModel, SequenceModel, SequenceItemModel
from services.cnc.cnc_service import CncService
from services.configurations.configurations_service import ConfigurationService
from services.port_manager.port_manager import PortManager

router = APIRouter(
    tags=["cnc"],
    prefix="/cnc"
)

# Helper Functions for CNC Routes
# These functions eliminate code duplication and centralize common patterns
# 
# REFACTORING SUMMARY:
# - Eliminated duplicate data structure conversion logic (lines 553-567, 623-636, 718-733, 789-804)
# - Consolidated array manipulation patterns (lines 575-583, 741-749) into reusable functions
# - Replaced manual configuration context setup with RouteHelper.setup_configuration_context()
# - Maintained exact same API interface and response formats
# - Preserved all WebSocket functionality and error handling

def convert_cnc_to_data_dict(cnc):
    """
    Convert CNC entity (dict or object) to standardized data dictionary.
    Handles both TinyDB format (dict) and object format consistently.
    
    Args:
        cnc: CNC entity from repository (dict or object)
        
    Returns:
        dict: Standardized CNC data dictionary
    """
    if isinstance(cnc, dict):
        return {
            'uid': cnc.get('uid'),
            'name': cnc.get('name'),
            'type': cnc.get('type'), 
            'port': cnc.get('port'),
            'sequences': cnc.get('sequences', []),
            'shortcuts': cnc.get('shortcuts', [])
        }
    else:
        return {
            'uid': getattr(cnc, 'uid', None),
            'name': getattr(cnc, 'name', None),
            'type': getattr(cnc, 'type', None),
            'port': getattr(cnc, 'port', None),
            'sequences': getattr(cnc, 'sequences', []),
            'shortcuts': getattr(cnc, 'shortcuts', [])
        }

def update_cnc_array_field(cnc_data: dict, field_name: str, new_item: dict, item_uid_key: str = 'uid'):
    """
    Update an array field in CNC data (sequences or shortcuts).
    Handles both adding new items and updating existing ones based on UID.
    
    Args:
        cnc_data: CNC data dictionary
        field_name: Name of the array field ('sequences' or 'shortcuts')
        new_item: Item to add or update
        item_uid_key: Key to use for finding existing items (default: 'uid')
        
    Returns:
        bool: True if item was updated, False if it was added as new
    """
    # Initialize field if not present
    if field_name not in cnc_data or cnc_data[field_name] is None:
        cnc_data[field_name] = []
    
    # Find existing item index
    existing_index = next((i for i, item in enumerate(cnc_data[field_name]) 
                          if item.get(item_uid_key) == new_item.get(item_uid_key)), None)
    
    if existing_index is not None:
        # Update existing item
        cnc_data[field_name][existing_index] = new_item
        return True  # Updated existing
    else:
        # Add new item
        cnc_data[field_name].append(new_item)
        return False  # Added new

def remove_cnc_array_item(cnc_data: dict, field_name: str, item_uid: str, item_uid_key: str = 'uid'):
    """
    Remove an item from a CNC array field by UID.
    
    Args:
        cnc_data: CNC data dictionary
        field_name: Name of the array field ('sequences' or 'shortcuts')
        item_uid: UID of item to remove
        item_uid_key: Key to use for finding items (default: 'uid')
        
    Returns:
        bool: True if item was found and removed, False otherwise
    """
    if field_name not in cnc_data or not cnc_data[field_name]:
        return False
        
    initial_length = len(cnc_data[field_name])
    cnc_data[field_name] = [item for item in cnc_data[field_name] 
                           if item.get(item_uid_key) != item_uid]
    
    return len(cnc_data[field_name]) < initial_length

def get_cnc_array_field(cnc, field_name: str):
    """
    Safely extract an array field from CNC entity.
    Handles different storage formats and ensures list return type.
    
    Args:
        cnc: CNC entity from repository
        field_name: Name of the array field to extract
        
    Returns:
        list: Array field content or empty list if not found
    """
    result = []
    
    if isinstance(cnc, dict):
        result = cnc.get(field_name, [])
    elif hasattr(cnc, field_name) and getattr(cnc, field_name) is not None:
        result = getattr(cnc, field_name)
    elif hasattr(cnc, '__dict__') and field_name in cnc.__dict__:
        result = cnc.__dict__[field_name] or []
    
    # Ensure we return a list
    return result if isinstance(result, list) else []


@router.get("")
async def get_cncs(
        cnc_repository: CncRepository = Depends(get_service_by_type(CncRepository)),
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
):
    # Setup configuration context using RouteHelper
    RouteHelper.setup_configuration_context(cnc_repository, configuration_service)
    
    return RouteHelper.list_entities(cnc_repository, "CNC")


@router.get("/check_ports")
async def check_ports(
        port_manager: PortManager = Depends(get_service_by_type(PortManager)),
):
    try:
        # Get only CNC-specific ports, excluding DMC readers and other device types
        return await port_manager.get_cnc_ports()
    except Exception as e:
        raise create_error_response(
            operation="check available ports",
            entity_type="Port Manager",
            exception=e
        )


@router.get("/cnc_types")
async def get_cnc_types(cnc_service: CncService = Depends(get_service_by_type(CncService))):
    return cnc_service.get_available_types()


@router.post("/initialize_all")
async def initialize_all_cncs(
        cnc_service: CncService = Depends(get_service_by_type(CncService))
):
    try:
        cnc_service.reinitialize_all_cncs()
        return RouteHelper.create_success_response("CNC re-initialization started")
    except Exception as e:
        raise create_error_response(
            operation="reinitialize all CNCs",
            entity_type="CNC Service",
            exception=e
        )


@router.post("/{cnc_uid}/initialize")
async def initialize_cnc(
        cnc_uid: str,
        cnc_service: CncService = Depends(get_service_by_type(CncService))
):
    try:
        cnc_service.create_cnc(cnc_uid)
        return RouteHelper.create_success_response(f"CNC {cnc_uid} initialized successfully")
    except Exception as e:
        raise create_error_response(
            operation="initialize CNC",
            entity_type="CNC",
            entity_id=cnc_uid,
            exception=e
        )


@router.post("/{cnc_uid}/deinitialize")
async def deinitialize_cnc(
        cnc_uid: str,
        cnc_service: CncService = Depends(get_service_by_type(CncService))
):
    try:
        cnc_service.delete_cnc(cnc_uid)
        return RouteHelper.create_success_response(f"CNC {cnc_uid} deinitialized successfully")
    except Exception as e:
        raise create_error_response(
            operation="deinitialize CNC",
            entity_type="CNC",
            entity_id=cnc_uid,
            exception=e
        )


@router.get("/{cnc_uid}")
async def get_cnc(
        cnc_uid: str,
        cnc_repository: CncRepository = Depends(get_service_by_type(CncRepository)),
):
    entity_data = RouteHelper.get_entity_by_id(cnc_repository, cnc_uid, "CNC")
    return CncModel(**entity_data)


@router.post("")
async def post_cnc(
        cnc_model: CncModel,
        user: dict = Depends(require_authentication("create CNC")),
        cnc_repository: CncRepository = Depends(get_service_by_type(CncRepository)),
        cnc_service: CncService = Depends(get_service_by_type(CncService))
):
    try:
        # Create in repository
        RouteHelper.create_entity(cnc_repository, cnc_model, "CNC")
        # Initialize in service
        cnc_service.create_cnc(cnc_model.uid)
        return RouteHelper.create_success_response(
            f"CNC {cnc_model.name} ({cnc_model.uid}) created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="create",
            entity_type="CNC",
            entity_id=f"{cnc_model.name} ({cnc_model.uid})",
            exception=e
        )


class CncListModel(BaseModel):
    cnc_list: list

@router.post("/save")
async def post_cncs(
        cnc_data: CncListModel,
        user: dict = Depends(require_authentication("save CNCs")),
        cnc_repository: CncRepository = Depends(get_service_by_type(CncRepository)),
        cnc_service: CncService = Depends(get_service_by_type(CncService))
):
    try:
        cnc_models = []
        for cnc in cnc_data.cnc_list:
            cnc_models.append(CncModel(**cnc))
        add, update, delete = cnc_service.save_cnc_configurations(cnc_models)
        for cnc_model in cnc_models:
            if cnc_model.uid in add:
                cnc_repository.create(cnc_model)
            if cnc_model.uid in update:
                cnc_repository.update(cnc_model)
        for cnc_uid in delete:
            cnc_repository.delete(cnc_uid)
        return RouteHelper.create_success_response("CNCs saved successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="save CNCs",
            entity_type="CNC Service",
            exception=e
        )


@router.put("")
async def put_cnc(
        cnc_model: CncModel,
        user: dict = Depends(require_authentication("update CNC")),
        cnc_repository: CncRepository = Depends(get_service_by_type(CncRepository)),
):
    return RouteHelper.update_entity(cnc_repository, cnc_model.model_dump(), "CNC")


@router.delete("/{cnc_uid}")
async def delete_cnc(
        cnc_uid: str,
        user: dict = Depends(require_authentication("delete CNC")),
        cnc_repository: CncRepository = Depends(get_service_by_type(CncRepository)),
):
    return RouteHelper.delete_entity(cnc_repository, cnc_uid, "CNC")


@router.get("/{cnc_uid}/__API__/abort")
async def abort_cnc(
        cnc_uid: str,
        cnc_service: CncService = Depends(get_service_by_type(CncService)),
):
    try:
        handle_cnc_operation_errors("abort", cnc_service, cnc_uid)
        cnc_service.abort(cnc_uid)
        return RouteHelper.create_success_response(f"Abort command executed on CNC {cnc_uid}")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="execute abort command",
            entity_type="CNC",
            entity_id=cnc_uid,
            exception=e
        )


@router.get("/{cnc_uid}/__API__/home")
async def home(
        cnc_uid: str,
        cnc_service: CncService = Depends(get_service_by_type(CncService)),
):
    try:
        handle_cnc_operation_errors("home", cnc_service, cnc_uid)
        await cnc_service.home(cnc_uid)
        return RouteHelper.create_success_response(f"Home command executed on CNC {cnc_uid}")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="execute home command",
            entity_type="CNC",
            entity_id=cnc_uid,
            exception=e
        )


@router.get("/{cnc_uid}/__API__/soft_reset")
async def soft_reset(
        cnc_uid: str,
        cnc_service: CncService = Depends(get_service_by_type(CncService)),
):
    try:
        handle_cnc_operation_errors("soft reset", cnc_service, cnc_uid)
        cnc_service.soft_reset(cnc_uid)
        return RouteHelper.create_success_response(f"Soft reset command executed on CNC {cnc_uid}")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="execute soft reset command",
            entity_type="CNC",
            entity_id=cnc_uid,
            exception=e
        )


@router.get("/{cnc_uid}/__API__/zero_reset")
async def zero_reset(
        cnc_uid: str,
        cnc_service: CncService = Depends(get_service_by_type(CncService)),
):
    try:
        handle_cnc_operation_errors("zero reset", cnc_service, cnc_uid)
        cnc_service.zero_reset(cnc_uid)
        return RouteHelper.create_success_response(f"Zero reset command executed on CNC {cnc_uid}")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="execute zero reset command",
            entity_type="CNC",
            entity_id=cnc_uid,
            exception=e
        )


@router.get("/{cnc_uid}/__API__/return_to_zero")
async def return_to_zero(
        cnc_uid: str,
        cnc_service: CncService = Depends(get_service_by_type(CncService)),
):
    try:
        handle_cnc_operation_errors("return to zero", cnc_service, cnc_uid)
        cnc_service.return_to_zero(cnc_uid)
        return RouteHelper.create_success_response(f"Return to zero command executed on CNC {cnc_uid}")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="execute return to zero command",
            entity_type="CNC",
            entity_id=cnc_uid,
            exception=e
        )


@router.get("/{cnc_uid}/__API__/unlock")
async def unlock(
        cnc_uid: str,
        cnc_service: CncService = Depends(get_service_by_type(CncService)),
):
    try:
        handle_cnc_operation_errors("unlock", cnc_service, cnc_uid)
        cnc_service.unlock(cnc_uid)
        return RouteHelper.create_success_response(f"Unlock command executed on CNC {cnc_uid}")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="execute unlock command",
            entity_type="CNC",
            entity_id=cnc_uid,
            exception=e
        )


@router.get("/{cnc_uid}/__API__/terminal")
async def terminal(
        cnc_uid: str,
        command: str,
        cnc_service: CncService = Depends(get_service_by_type(CncService)),
):
    try:
        handle_cnc_operation_errors("terminal command", cnc_service, cnc_uid)
        cnc_service.send(cnc_uid, command)
        return RouteHelper.create_success_response(f"Terminal command '{command}' executed on CNC {cnc_uid}")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation=f"send terminal command '{command}'",
            entity_type="CNC",
            entity_id=cnc_uid,
            exception=e
        )


@router.get("/{cnc_uid}/__API__/{axis}/minus")
async def axis_minus(
        cnc_uid: str,
        axis,
        feed_rate,
        step,
        cnc_service: CncService = Depends(get_service_by_type(CncService)),
):
    try:
        handle_cnc_operation_errors("axis minus movement", cnc_service, cnc_uid)
        cnc_service.axis_minus(uid=cnc_uid, axis=axis, step=step, feed_rate=feed_rate)
        return RouteHelper.create_success_response(f"Axis {axis} minus movement executed on CNC {cnc_uid}")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation=f"move axis {axis} minus by {step} steps at feed rate {feed_rate}",
            entity_type="CNC",
            entity_id=cnc_uid,
            exception=e
        )


@router.get("/{cnc_uid}/__API__/{axis}/plus")
async def axis_plus(
        cnc_uid: str,
        axis,
        feed_rate,
        step,
        cnc_service: CncService = Depends(get_service_by_type(CncService)),
):
    try:
        handle_cnc_operation_errors("axis plus movement", cnc_service, cnc_uid)
        cnc_service.axis_plus(uid=cnc_uid, axis=axis, step=step, feed_rate=feed_rate)
        return RouteHelper.create_success_response(f"Axis {axis} plus movement executed on CNC {cnc_uid}")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation=f"move axis {axis} plus by {step} steps at feed rate {feed_rate}",
            entity_type="CNC",
            entity_id=cnc_uid,
            exception=e
        )


@router.get("/{cnc_uid}/__API__/{location_uid}/move_to_location")
async def move_to_location(
        cnc_uid: str,
        location_uid: str,
        block: bool,
        timeout: int,
        cnc_service: CncService = Depends(get_service_by_type(CncService)),
        location_repository: LocationRepository = Depends(get_service_by_type(LocationRepository)),
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
):
    try:
        # Setup configuration context using RouteHelper
        RouteHelper.setup_configuration_context(location_repository, configuration_service)
            
        handle_cnc_operation_errors("move to location", cnc_service, cnc_uid)
        location = LocationModel(**location_repository.read_id(location_uid))
        await cnc_service.move_to_location(cnc_uid, location, block, timeout)
        return RouteHelper.create_success_response(f"Move to location command executed on CNC {cnc_uid}")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation=f"move to location {location_uid}",
            entity_type="CNC",
            entity_id=cnc_uid,
            exception=e
        )


manager = ConnectionManager()


@router.websocket("/{cnc_uid}/ws")
async def ws_cnc(
        websocket: WebSocket, cnc_uid,
        cnc_service: CncService = Depends(get_service_by_type(CncService)),
):
    try:
        await manager.connect(cnc_uid, websocket)
        cnc_info = cnc_service.get_cnc_info(cnc_uid)
        
        # Send initial connection status
        if cnc_info.get('is_mock', False):
            connection_error = cnc_info.get('connection_error', 'Unknown connection error')
            is_cross_platform_issue = connection_error.startswith('Cross-platform:')
            
            await websocket.send_json({
                'event': 'connection_error',
                'message': f'CNC {cnc_info.get("name", cnc_uid)} is not connected',
                'error': connection_error,
                'port': cnc_info.get('port', 'Unknown'),
                'type': cnc_info.get('type', 'Unknown'),
                'name': cnc_info.get('name', cnc_uid),
                'is_cross_platform_issue': is_cross_platform_issue,
                'cnc_uid': cnc_uid
            })
        else:
            await websocket.send_json({
                'event': 'connection_success',
                'message': f'CNC {cnc_info.get("name", cnc_uid)} connected successfully',
                'port': cnc_info.get('port', 'Unknown'),
                'type': cnc_info.get('type', 'Unknown')
            })
        
        while True:
            if manager.is_closed(cnc_uid):
                break

            msg = cnc_service.read_callback_buffer(cnc_uid)
            while msg:
                await websocket.send_json(msg)
                msg = cnc_service.read_callback_buffer(cnc_uid)

            # Reduced to 20ms for faster sequence state updates
            if not await manager.safe_sleep_with_cancellation(0.02):
                break  # Cancelled, exit loop
        await manager.disconnect(cnc_uid)
    except WebSocketDisconnect:
        await manager.disconnect(cnc_uid)
    except LocalProtocolError as e:
        print(f"WebSocket protocol error for CNC {cnc_uid}: {e}")
        manager.remove_websocket(cnc_uid)
    except asyncio.CancelledError:
        # Handle cancellation during shutdown
        manager.remove_websocket(cnc_uid)
    except RuntimeError as e:
        print(f"WebSocket runtime error for CNC {cnc_uid}: {e}")
    except Exception as e:
        print(f"Unexpected WebSocket error for CNC {cnc_uid}: {e}")
        try:
            await websocket.send_json({
                'event': 'websocket_error',
                'message': f'WebSocket connection error for CNC {cnc_uid}',
                'error': str(e)
            })
        except:
            pass
    finally:
        await manager.disconnect(cnc_uid)


@router.post("/{cnc_uid}/ws/close")
async def close_ws(cnc_uid):
    await manager.connection_closed(cnc_uid)
    return JSONResponse(status_code=status.HTTP_200_OK, content='')


# Position Sequence Endpoints
@router.get("/{cnc_uid}/sequences")
async def get_sequences(
    cnc_uid: str,
    cnc_repository: CncRepository = Depends(get_service_by_type(CncRepository)),
    configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
):
    """Get all saved sequences for a specific CNC"""
    try:
        # Setup configuration context using RouteHelper
        RouteHelper.setup_configuration_context(cnc_repository, configuration_service)
        
        cnc = cnc_repository.read_id(cnc_uid)
        if not cnc:
            raise HTTPException(status_code=404, detail=f"CNC {cnc_uid} not found")
        
        # Use helper function to extract sequences
        sequences = get_cnc_array_field(cnc, 'sequences')
        return JSONResponse(status_code=200, content=sequences)
    except UidNotFound:
        raise HTTPException(status_code=404, detail=f"CNC {cnc_uid} not found")
    except Exception as e:
        print(f"[SEQUENCE] Error getting sequences for CNC {cnc_uid}: {e}")
        print(f"[SEQUENCE] Exception type: {type(e)}")
        # Return empty list instead of error to avoid breaking the frontend
        return JSONResponse(status_code=200, content=[])


@router.post("/{cnc_uid}/sequences")
async def save_sequence(
    cnc_uid: str,
    sequence: dict,
    cnc_repository: CncRepository = Depends(get_service_by_type(CncRepository)),
    configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
):
    """Save or update a sequence for a specific CNC"""
    try:
        # Setup configuration context using RouteHelper
        RouteHelper.setup_configuration_context(cnc_repository, configuration_service)
        
        cnc = cnc_repository.read_id(cnc_uid)
        if not cnc:
            raise HTTPException(status_code=404, detail=f"CNC {cnc_uid} not found")
        
        # Convert CNC entity to standardized data dictionary
        cnc_data = convert_cnc_to_data_dict(cnc)
        
        # Update sequences array using helper function
        was_updated = update_cnc_array_field(cnc_data, 'sequences', sequence)
        
        # Use RouteHelper for consistent updating
        result = RouteHelper.update_entity(cnc_repository, cnc_data, "CNC")
        
        # Return sequence-specific response
        action = "updated" if was_updated else "added"
        return JSONResponse(status_code=200, content={
            "message": f"Sequence {action} successfully",
            "sequence": sequence
        })
    except UidNotFound:
        raise HTTPException(status_code=404, detail=f"CNC {cnc_uid} not found")
    except Exception as e:
        print(f"[SEQUENCE] Error saving sequence: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{cnc_uid}/sequences/{sequence_uid}")
async def delete_sequence(
    cnc_uid: str,
    sequence_uid: str,
    cnc_repository: CncRepository = Depends(get_service_by_type(CncRepository)),
    configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
):
    """Delete a sequence for a specific CNC"""
    try:
        # Setup configuration context using RouteHelper
        RouteHelper.setup_configuration_context(cnc_repository, configuration_service)
        
        cnc = cnc_repository.read_id(cnc_uid)
        if not cnc:
            raise HTTPException(status_code=404, detail=f"CNC {cnc_uid} not found")
        
        # Check if sequences exist before attempting deletion
        sequences = get_cnc_array_field(cnc, 'sequences')
        if not sequences:
            raise HTTPException(status_code=404, detail="No sequences found")
        
        # Convert CNC entity to standardized data dictionary
        cnc_data = convert_cnc_to_data_dict(cnc)
        
        # Remove sequence using helper function
        was_removed = remove_cnc_array_item(cnc_data, 'sequences', sequence_uid)
        
        if not was_removed:
            raise HTTPException(status_code=404, detail=f"Sequence {sequence_uid} not found")
        
        # Use RouteHelper for consistent updating
        result = RouteHelper.update_entity(cnc_repository, cnc_data, "CNC")
        
        return JSONResponse(status_code=200, content={
            "message": "Sequence deleted successfully"
        })
    except UidNotFound:
        raise HTTPException(status_code=404, detail=f"CNC {cnc_uid} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Shortcuts Endpoints (similar to sequences)
@router.get("/{cnc_uid}/shortcuts")
async def get_shortcuts(
    cnc_uid: str,
    cnc_repository: CncRepository = Depends(get_service_by_type(CncRepository)),
    configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
):
    """Get all saved shortcuts for a specific CNC"""
    try:
        # Setup configuration context using RouteHelper
        RouteHelper.setup_configuration_context(cnc_repository, configuration_service)
        
        cnc = cnc_repository.read_id(cnc_uid)
        if not cnc:
            raise HTTPException(status_code=404, detail=f"CNC {cnc_uid} not found")
        
        # Use helper function to extract shortcuts
        shortcuts = get_cnc_array_field(cnc, 'shortcuts')
        return JSONResponse(status_code=200, content=shortcuts)
    except UidNotFound:
        raise HTTPException(status_code=404, detail=f"CNC {cnc_uid} not found")
    except Exception as e:
        print(f"[SHORTCUT] Error getting shortcuts for CNC {cnc_uid}: {e}")
        print(f"[SHORTCUT] Exception type: {type(e)}")
        # Return empty list instead of error to avoid breaking the frontend
        return JSONResponse(status_code=200, content=[])


@router.post("/{cnc_uid}/shortcuts")
async def save_shortcut(
    cnc_uid: str,
    shortcut: dict,
    cnc_repository: CncRepository = Depends(get_service_by_type(CncRepository)),
    configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
):
    """Save or update shortcuts for a specific CNC"""
    try:
        # Setup configuration context using RouteHelper
        RouteHelper.setup_configuration_context(cnc_repository, configuration_service)
        
        cnc = cnc_repository.read_id(cnc_uid)
        if not cnc:
            raise HTTPException(status_code=404, detail=f"CNC {cnc_uid} not found")
        
        # Convert CNC entity to standardized data dictionary
        cnc_data = convert_cnc_to_data_dict(cnc)
        
        # Update shortcuts array using helper function
        was_updated = update_cnc_array_field(cnc_data, 'shortcuts', shortcut)
        
        # Use RouteHelper for consistent updating
        result = RouteHelper.update_entity(cnc_repository, cnc_data, "CNC")
        
        # Return shortcut-specific response
        action = "updated" if was_updated else "added"
        return JSONResponse(status_code=200, content={
            "message": f"Shortcut {action} successfully",
            "shortcut": shortcut
        })
    except UidNotFound:
        raise HTTPException(status_code=404, detail=f"CNC {cnc_uid} not found")
    except Exception as e:
        print(f"[SHORTCUT] Error saving shortcut: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{cnc_uid}/shortcuts/{shortcut_uid}")
async def delete_shortcut(
    cnc_uid: str,
    shortcut_uid: str,
    cnc_repository: CncRepository = Depends(get_service_by_type(CncRepository)),
    configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
):
    """Delete shortcuts for a specific CNC"""
    try:
        # Setup configuration context using RouteHelper
        RouteHelper.setup_configuration_context(cnc_repository, configuration_service)
        
        cnc = cnc_repository.read_id(cnc_uid)
        if not cnc:
            raise HTTPException(status_code=404, detail=f"CNC {cnc_uid} not found")
        
        # Check if shortcuts exist before attempting deletion
        shortcuts = get_cnc_array_field(cnc, 'shortcuts')
        if not shortcuts:
            raise HTTPException(status_code=404, detail="No shortcuts found")
        
        # Convert CNC entity to standardized data dictionary
        cnc_data = convert_cnc_to_data_dict(cnc)
        
        # Remove shortcut using helper function
        was_removed = remove_cnc_array_item(cnc_data, 'shortcuts', shortcut_uid)
        
        if not was_removed:
            raise HTTPException(status_code=404, detail=f"Shortcut {shortcut_uid} not found")
        
        # Use RouteHelper for consistent updating
        result = RouteHelper.update_entity(cnc_repository, cnc_data, "CNC")
        
        return JSONResponse(status_code=200, content={
            "message": "Shortcut deleted successfully"
        })
    except UidNotFound:
        raise HTTPException(status_code=404, detail=f"CNC {cnc_uid} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))