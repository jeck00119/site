from collections import deque
from typing import Union
from unittest.mock import Mock
import time

from serial import SerialException

from repo.repositories import CncRepository, LocationRepository
from services.cnc.cnc_machine_gerbil import CncMachineGerbil
from services.cnc.cnc_machine_marlin import CncMachineMarlin
from services.cnc.cnc_models import CncModel, LocationModel
from services.cnc.cnc_error_handler import CncErrorHandler
from src.metaclasses.singleton import Singleton
import logging


class CncService(metaclass=Singleton):
    def __init__(self):
        self._cnc_repo = CncRepository()
        self._location_repo = LocationRepository()
        self._cnc_objects: dict[str, Union[CncMachineGerbil, CncMachineMarlin, Mock]] = {}
        self._callbacks_buffers: dict[str, deque] = {}
        self._exceptions: list = []
        self._connection_errors: dict[str, str] = {}  # Track connection errors per CNC
        # Use centralized error handler
        self._error_handler = CncErrorHandler()
        self.logger = logging.getLogger(__name__)
        
        # Message batching configuration - optimized for sequence responsiveness
        self._batch_buffers: dict[str, list] = {}
        self._last_batch_time: dict[str, float] = {}
        # Reduced batching for faster sequence state updates
        self._batch_interval = 0.02  # 20ms batching interval for faster sequence detection
        self._max_batch_size = 5     # Smaller batches for quicker processing

    @staticmethod
    def get_available_types():
        return ["GRBL", "FluidNC", "Marlin"]
    
    def _sync_validate_port(self, port_manager, port: str, expected_device_type: str):
        """Synchronous port validation - fallback when async fails"""
        try:
            import serial.tools.list_ports
            
            # Device type names mapping
            device_type_names = {
                'cncs': 'CNC machine',
                'dmc_readers': 'DMC reader (Cognex)',
                'ultra_arm_robots': 'Ultra Arm robot',
                'cameras': 'camera device',
                'profilometers': 'profilometer (Keyence/SICK)',
            }
            
            # Get the actual port name (remove description if present)
            actual_port = port.split('(')[0].strip() if '(' in port else port
            expected_name = device_type_names.get(expected_device_type, expected_device_type)
            
            result = {
                'is_valid': False,
                'is_correct_device_type': False,
                'expected_device_type': expected_device_type,
                'expected_device_name': expected_name,
                'actual_device_types': [],
                'actual_device_name': '',
                'device_description': '',
                'error_message': '',
                'suggested_action': '',
                'port': actual_port
            }
            
            # Find the device using synchronous serial port listing
            port_device = None
            for comport in serial.tools.list_ports.comports():
                if comport.device == actual_port:
                    device_info = port_manager._create_device_info(comport)
                    port_device = device_info
                    break
            
            if port_device:
                device_types = port_device['device_types']
                result['actual_device_types'] = device_types
                result['device_description'] = port_device['description']
                
                # Check if port has the expected device type
                if expected_device_type in device_types:
                    result['is_valid'] = True
                    result['is_correct_device_type'] = True
                    result['error_message'] = f"Port {actual_port} validated as {expected_name}"
                else:
                    result['is_valid'] = False
                    result['is_correct_device_type'] = False
                    
                    # Determine what device type is actually connected
                    if 'dmc_readers' in device_types:
                        result['actual_device_name'] = 'DMC reader (Cognex)'
                    elif 'cncs' in device_types:
                        result['actual_device_name'] = 'CNC machine'
                    elif 'ultra_arm_robots' in device_types:
                        result['actual_device_name'] = 'Ultra Arm robot'
                    elif 'profilometers' in device_types:
                        result['actual_device_name'] = 'profilometer (Keyence/SICK)'
                    elif 'cameras' in device_types:
                        result['actual_device_name'] = 'camera device'
                    else:
                        result['actual_device_name'] = ', '.join(device_types) if device_types else 'unknown device'
                    
                    result['error_message'] = (
                        f"Configuration mismatch: Expected {expected_name} on port {actual_port}, "
                        f"but found {result['actual_device_name']} instead"
                    )
                    result['suggested_action'] = f"Please update configuration to use the correct port for {expected_name}"
            else:
                result['error_message'] = f"Port {actual_port} not found or not connected"
                result['suggested_action'] = f"Check if {expected_name} is connected and try again"
                
            return result
            
        except Exception as e:
            self.logger.error(f"Sync validation failed: {e}")
            return {
                'is_valid': False,
                'error_message': f"Port validation failed: {str(e)}",
                'suggested_action': "Connection will be attempted anyway"
            }

    def start_cnc_service(self):
        pass

    def shutdown_cnc_service(self):
        """Shutdown all CNC connections and clean up resources"""
        try:
            self.logger.info("Shutting down CNC service...")
            active_cnc_uids = list(self._cnc_objects.keys())
            for uid in active_cnc_uids:
                try:
                    self.logger.debug(f"Disconnecting CNC {uid}")
                    self._deinit_cnc(uid)
                except Exception as e:
                    self.logger.error(f"Error disconnecting CNC {uid}: {e}")
            
            # Clear all data structures
            self._cnc_objects.clear()
            self._callbacks_buffers.clear()
            self._batch_buffers.clear()
            self._last_batch_time.clear()
            self._connection_errors.clear()
            
            self.logger.info("CNC service shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during CNC service shutdown: {e}")

    def reinitialize_all_cncs(self):
        active_cnc_uids = list(self._cnc_objects.keys())
        for uid in active_cnc_uids:
            self._deinit_cnc(uid)

        self.initialize_all_cncs()

    def initialize_all_cncs(self):
        cncs = self._cnc_repo.read_all()
        self.logger.info(f"initialize_all_cncs: Found {len(cncs)} CNCs to initialize")
        for cnc in cncs:
            try:
                if cnc['uid'] not in self._callbacks_buffers:
                    self._callbacks_buffers[cnc['uid']] = deque(maxlen=20)
                    self.logger.info(f"Initialized callback buffer for CNC {cnc['uid']}")
                self._init_cnc(cnc['uid'])
            except Exception as e:
                cnc_name = cnc.get("name", cnc.get("uid"))
                cnc_uid = cnc.get("uid")
                error_msg = f"Could not initialize CNC {cnc_name}: {e}"
                self.logger.error(error_msg)
                self._connection_errors[cnc_uid] = str(e)

    def _callback(self, uid, *data):
        if uid in self._callbacks_buffers:
            self._callbacks_buffers[uid].append(data)

    def read_callback_buffer(self, uid):
        """Read callback buffer with message batching optimization"""
        cnc_type = self._get_cnc_type(uid)
        current_time = time.time()
        
        # Initialize batch buffer if not exists
        if uid not in self._batch_buffers:
            self._batch_buffers[uid] = []
            self._last_batch_time[uid] = current_time
        
        # Collect messages from the callback buffer
        messages_collected = []
        while self._callbacks_buffers.get(uid) and self._callbacks_buffers[uid]:
            buffed = self._callbacks_buffers[uid].popleft()
            # Unwrap nested tuple if needed - callback data comes as (('event', data...),)
            if len(buffed) == 1 and isinstance(buffed[0], tuple):
                buffed = buffed[0]
            event = buffed[0]
            
            message = self._format_message(event, buffed, cnc_type)
            # Only add non-None messages (filters out simple "ok" messages)
            if message is not None:
                messages_collected.append(message)
        
        # Add collected messages to batch buffer
        self._batch_buffers[uid].extend(messages_collected)
        
        
        # Check if we should send a batch
        time_since_last_batch = current_time - self._last_batch_time[uid]
        should_send_batch = (
            len(self._batch_buffers[uid]) >= self._max_batch_size or
            (len(self._batch_buffers[uid]) > 0 and time_since_last_batch >= self._batch_interval) or
            self._has_priority_message(self._batch_buffers[uid])
        )
        
        if should_send_batch and self._batch_buffers[uid]:
            batch = self._batch_buffers[uid].copy()
            self._batch_buffers[uid].clear()
            self._last_batch_time[uid] = current_time
            
            
            # Return batch or single message based on size
            if len(batch) == 1:
                return batch[0]
            else:
                return {'event': 'batch', 'messages': batch}
        
        return None
    
    def _format_message(self, event, buffed, cnc_type):
        """Format individual message based on event type"""
        if event == "on_stateupdate":
            state = buffed[1]
            m_pos = buffed[2]
            w_pos = buffed[3]
            return {'event': event, 'state': state, 'mPos': m_pos, 'wPos': w_pos}

        elif event in ["on_idle", "on_read", "on_alarm"]:
            message_content = buffed[1]
            
            # Filter out simple "ok" messages from on_read to reduce terminal spam
            # But keep important responses like "echo:", error messages, etc.
            if event == "on_read":
                stripped_msg = message_content.strip().lower()
                # Only filter simple "ok" responses, not important messages
                if stripped_msg == "ok":
                    return None  # Don't send simple "ok" messages to terminal
                # Always show echo messages (M503 responses), errors, etc.
            
            return {'event': event, "message": message_content}

        elif event == "on_settings_downloaded":
            return {'event': event, "message": buffed[1]}

        elif event == "on_error":
            error_message = self._error_handler.get_error_message(cnc_type, buffed[1])
            return {'event': event, "message": error_message}

        elif event == "connection_error":
            connection_error = buffed[1]
            is_cross_platform_issue = buffed[2]
            cnc_uid = buffed[3]
            self.logger.info(f"Formatting connection_error message for CNC {cnc_uid}")
            return {
                'event': 'connection_error',
                'message': f'CNC connection failed',
                'error': connection_error,
                'is_cross_platform_issue': is_cross_platform_issue,
                'cnc_uid': cnc_uid
            }

        elif event in ["on_job_completed", "on_movement", "on_standstill", "on_boot", "on_write", "on_feed_change", "on_connection_ready"]:
            return {'event': event}

        else:
            message = str(buffed[1:]) if len(buffed) > 1 else ''
            return {'event': event, 'message': message}
    
    def _has_priority_message(self, messages):
        """Check if batch contains priority messages that should be sent immediately"""
        priority_events = ["on_error", "on_alarm", "on_job_completed", "on_boot", "on_connection_ready", "connection_error"]
        return any(msg.get('event') in priority_events for msg in messages)

    def _get_cnc_type(self, uid):
        try:
            cnc = self._cnc_repo.read_id(uid)
            return cnc.get('type', 'GRBL')
        except Exception:
            return 'GRBL'

    def update_cncs(self, cnc_models: list, initialize_connections=True):
        """Update CNCs with option to skip connection initialization"""
        saved_cncs = self._cnc_repo.read_all()
        found_axis = {}
        for cnc in saved_cncs:
            found_axis[cnc["uid"]] = False
        saved_uids = list(found_axis.keys())
        update = []
        delete = []
        add = []
        
        for cnc_model in cnc_models:
            if cnc_model.uid in saved_uids:
                found_axis[cnc_model.uid] = True
                # Only check port changes and reinitialize if we're doing connection initialization
                if initialize_connections and cnc_model.port != self._cnc_objects.get(cnc_model.uid, Mock()).get_port():
                    self._deinit_cnc(cnc_model.uid)
                    self._init_cnc_from_model(cnc_model)
                    update.append(cnc_model.uid)
                elif initialize_connections:
                    # CNC exists but we're initializing - make sure it's connected
                    if cnc_model.uid not in self._cnc_objects:
                        self._init_cnc_from_model(cnc_model)
                        update.append(cnc_model.uid)
            else:
                # New CNC - only initialize connection if requested
                if initialize_connections:
                    self._init_cnc_from_model(cnc_model)
                add.append(cnc_model.uid)
                
        for axis_uid, found in found_axis.items():
            if not found:
                if initialize_connections:
                    self._deinit_cnc(axis_uid)
                delete.append(axis_uid)
                
        return add, update, delete
    
    def save_cnc_configurations(self, cnc_models: list):
        """Save CNC configurations without attempting connections"""
        self.logger.info("Saving CNC configurations without initializing connections")
        return self.update_cncs(cnc_models, initialize_connections=False)

    def _init_cnc_from_model(self, cnc_model):
        self._callbacks_buffers[cnc_model.uid] = deque(maxlen=100)
        if cnc_model.type == "Marlin":
            self.logger.debug("MAAAAAAAAAAAAAAAAAAAAAAAAAAAAARLIN")
            self._cnc_objects[cnc_model.uid] = CncMachineMarlin(
                port=cnc_model.port,
                cnc_name=cnc_model.name,
                callback=lambda *vars: self._callback(cnc_model.uid, vars)
            )
        else:
            self.logger.debug("GRBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBL")
            self._cnc_objects[cnc_model.uid] = CncMachineGerbil(
                port=cnc_model.port,
                cnc_name=cnc_model.name,
                callback=lambda *vars: self._callback(cnc_model.uid, vars)
            )
        
        # VALIDATE PORT TYPE BEFORE CONNECTION
        try:
            from services.port_manager.port_manager import UnifiedUSBManager
            import asyncio
            
            port_manager = UnifiedUSBManager()
            
            # Use the existing event loop if available, otherwise create a new one
            try:
                # Try to get current event loop
                loop = asyncio.get_running_loop()
                # If we have a running loop, use asyncio.create_task (but we can't await here)
                # So we'll use a synchronous approach instead
                raise RuntimeError("Running loop detected, use sync approach")
            except RuntimeError:
                # No running loop, we can create one
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        validation_result = loop.run_until_complete(port_manager.validate_port_for_device_type(cnc_model.port, 'cncs'))
                    finally:
                        # Properly close the loop to prevent warnings
                        loop.close()
                        asyncio.set_event_loop(None)
                except Exception as async_error:
                    self.logger.warning(f"CNC {cnc_model.uid}: Async validation failed ({async_error}), using sync validation")
                    # Fall back to synchronous validation
                    validation_result = self._sync_validate_port(port_manager, cnc_model.port, 'cncs')
            
            self.logger.info(f"CNC {cnc_model.uid}: {validation_result['error_message']}")
            
            if not validation_result['is_valid']:
                error_msg = f"{validation_result['error_message']}. {validation_result['suggested_action']}"
                self.logger.warning(f"CNC {cnc_model.uid}: {error_msg}")
                self._callback(cnc_model.uid, ('connection_error', error_msg, True, cnc_model.uid))
                
                # Store connection error and set mock object
                self._connection_errors[cnc_model.uid] = error_msg
                self._cnc_objects[cnc_model.uid] = Mock()
                raise SerialException(error_msg)
        
        except ImportError:
            self.logger.warning(f"CNC {cnc_model.uid}: Port manager not available - skipping port validation")
        except Exception as validation_error:
            self.logger.warning(f"CNC {cnc_model.uid}: Port validation failed: {validation_error} - attempting connection anyway")
        
        # PROCEED WITH CONNECTION IF VALIDATION PASSED
        try:
            self._cnc_objects[cnc_model.uid].init()
        except SerialException as e:
            # Check if this is a cross-platform port issue
            try:
                from services.port_manager.port_manager import UnifiedUSBManager
                port_manager = UnifiedUSBManager()
                
                current_platform = port_manager.get_current_platform()
                port = cnc_model.port
                is_cross_platform_issue = False
                
                if current_platform == 'windows':
                    if port.startswith('/dev/tty'):
                        is_cross_platform_issue = True
                elif current_platform in ['linux', 'macos']:
                    if port.startswith('COM'):
                        is_cross_platform_issue = True
                
                if is_cross_platform_issue:
                    error_msg = f"Cross-platform: Port '{port}' is configured for {'Linux/macOS' if current_platform == 'windows' else 'Windows'} but you're running on {current_platform.title()}. Available ports can be found in the CNC settings."
                    self.logger.warning(f"CNC {cnc_model.uid}: Cross-platform port issue - {error_msg}")
                    # Send cross-platform error to UI
                    self._callback(cnc_model.uid, ('connection_error', error_msg, True, cnc_model.uid))
                else:
                    self.logger.error(f"Could not connect to {port} - {str(e)}")
                    # Send generic connection error to UI
                    self._callback(cnc_model.uid, ('connection_error', f"Could not connect to {port}: {str(e)}", False, cnc_model.uid))
                    
            except Exception as validation_error:
                self.logger.error(f"Error during port validation: {validation_error}")
                self.logger.error(f"Could not connect to {cnc_model.port} - {str(e)}")
                self._callback(cnc_model.uid, ('connection_error', f"Could not connect to {cnc_model.port}: {str(e)}", False, cnc_model.uid))
            
            # Store connection error
            self._connection_errors[cnc_model.uid] = str(e)
            
            # Remove failed CNC from objects but keep in callbacks for error reporting
            if cnc_model.uid in self._cnc_objects:
                del self._cnc_objects[cnc_model.uid]
            
            # Put a Mock object to indicate failed connection
            self._cnc_objects[cnc_model.uid] = Mock()
            
            # Re-raise the exception so _init_cnc and create_cnc can handle it
            raise

    def _init_cnc(self, uid):
        if uid not in self._cnc_objects.keys():
            doc = self._cnc_repo.read_id(uid)
            cnc_model: CncModel = CncModel(**doc)
            try:
                self._init_cnc_from_model(cnc_model)
            except SerialException as e:
                # Check if this is a cross-platform port issue using existing validation
                try:
                    from services.port_manager.port_manager import UnifiedUSBManager
                    port_manager = UnifiedUSBManager()
                    
                    # Use synchronous platform detection instead of async validation
                    current_platform = port_manager.get_current_platform()
                    port = cnc_model.port
                    is_cross_platform_issue = False
                    platform_msg = ""
                    
                    # Check for cross-platform port patterns
                    if current_platform == 'windows' and (port.startswith('/dev/tty') or port.startswith('/dev/cu.')):
                        is_cross_platform_issue = True
                        platform_msg = f"Port '{port}' is configured for Linux/macOS but you're running on Windows"
                    elif current_platform == 'linux' and port.upper().startswith('COM'):
                        is_cross_platform_issue = True
                        platform_msg = f"Port '{port}' is configured for Windows but you're running on Linux"
                    elif current_platform == 'macos' and (port.upper().startswith('COM') or port.startswith('/dev/ttyACM')):
                        is_cross_platform_issue = True
                        platform_msg = f"Port '{port}' is configured for Windows/Linux but you're running on macOS"
                    
                    if is_cross_platform_issue:
                        error_msg = f"{platform_msg}. Available ports can be found in the CNC settings."
                        self.logger.error(f"CNC {uid}: Cross-platform port issue - {error_msg}")
                        self._connection_errors[uid] = f"Cross-platform: {error_msg}"
                    else:
                        error_msg = f"Serial connection failed: {e}"
                        self.logger.error(f"CNC {uid}: {error_msg}")
                        self._connection_errors[uid] = error_msg
                except Exception as validation_error:
                    # Fallback to original error handling if validation fails
                    self.logger.debug(f"Port validation failed: {validation_error}")
                    error_msg = f"Serial connection failed: {e}"
                    self.logger.error(f"CNC {uid}: {error_msg}")
                    self._connection_errors[uid] = error_msg
                
                self._cnc_objects[uid] = Mock()
                
                # Send connection error through callback buffer so WebSocket can pick it up
                if uid in self._callbacks_buffers:
                    connection_error = self._connection_errors.get(uid, 'Unknown connection error')
                    is_cross_platform_issue = connection_error.startswith('Cross-platform:')
                    
                    self.logger.info(f"Adding connection_error to callback buffer for CNC {uid}: {connection_error}")
                    # Format as expected by callback buffer - match the normal callback pattern
                    callback_data = ('connection_error', connection_error, is_cross_platform_issue, uid)
                    self._callbacks_buffers[uid].append(callback_data)
            except Exception as e:
                error_msg = f"Initialization failed: {e}"
                self.logger.error(f"CNC {uid}: {error_msg}")
                self._connection_errors[uid] = error_msg
                self._cnc_objects[uid] = Mock()
                
                # Send connection error through callback buffer so WebSocket can pick it up
                if uid in self._callbacks_buffers:
                    connection_error = self._connection_errors.get(uid, 'Unknown connection error')
                    is_cross_platform_issue = connection_error.startswith('Cross-platform:')
                    
                    self.logger.info(f"Adding connection_error to callback buffer for CNC {uid}: {connection_error}")
                    # Format as expected by callback buffer - match the normal callback pattern
                    callback_data = ('connection_error', connection_error, is_cross_platform_issue, uid)
                    self._callbacks_buffers[uid].append(callback_data)

    def _deinit_cnc(self, uid):
        if uid not in self._cnc_objects.keys():
            return
        else:
            if hasattr(self._cnc_objects[uid], 'disconnect'):
                self._cnc_objects[uid].disconnect()
            self._cnc_objects.pop(uid)
            self._callbacks_buffers.pop(uid, None)

    def create_cnc(self, cnc_uid):
        self._init_cnc(cnc_uid)
        # Check if connection failed and raise exception to inform the API
        if cnc_uid in self._cnc_objects and isinstance(self._cnc_objects[cnc_uid], Mock):
            connection_error = self._connection_errors.get(cnc_uid, 'Unknown connection error')
            # Pass through the detailed validation error message directly to the frontend
            raise Exception(connection_error)

    def update_cnc(self, cnc_uid):
        self._deinit_cnc(cnc_uid)
        self._init_cnc(cnc_uid)

    def delete_cnc(self, cnc_uid):
        self._deinit_cnc(cnc_uid)

    def _execute_cnc_command(self, uid, operation, *args, **kwargs):
        """Centralized validation and execution for all CNC operations"""
        if uid not in self._cnc_objects:
            raise Exception(f"CNC {uid} not found")
        
        cnc_obj = self._cnc_objects[uid]
        if isinstance(cnc_obj, Mock):
            connection_error = self._connection_errors.get(uid, 'Unknown connection error')
            raise Exception(f"CNC {uid} is not connected (Mock object). Connection error: {connection_error}")
        
        # Execute the operation
        method = getattr(cnc_obj, operation)
        if kwargs:
            return method(*args, **kwargs)
        else:
            return method(*args)

    def abort(self, uid):
        try:
            cnc_obj = self._cnc_objects.get(uid)
            if cnc_obj and hasattr(cnc_obj, '_abort_requested'):
                cnc_obj._abort_requested = True
            self._execute_cnc_command(uid, 'abort')
        except Exception as e:
            error_msg = f"Error during abort on CNC {uid}: {str(e)}"
            self.logger.error(error_msg)
            self._exceptions.append(error_msg)
            raise e

    async def home(self, uid):
        await self._execute_cnc_command(uid, 'home')

    def soft_reset(self, uid):
        self._execute_cnc_command(uid, 'soft_reset')

    def zero_reset(self, uid):
        self._execute_cnc_command(uid, 'zero_reset')

    def return_to_zero(self, uid):
        self._execute_cnc_command(uid, 'return_to_zero')

    def unlock(self, uid):
        self._execute_cnc_command(uid, 'unlock')

    def send(self, uid, command):
        self.logger.debug(f"Received command service: {command}")
        self._execute_cnc_command(uid, 'send', command)

    def axis_minus(self, uid, axis, step, feed_rate):
        kwargs = {'feed_rate': int(feed_rate)}
        if axis in ['x', 'X']:
            kwargs['x'] = -int(step)
        elif axis in ['y', 'Y']:
            kwargs['y'] = -int(step)
        elif axis in ['z', 'Z']:
            kwargs['z'] = -int(step)
        self._execute_cnc_command(uid, 'move_by', **kwargs)

    def axis_plus(self, uid, axis, step, feed_rate):
        kwargs = {'feed_rate': int(feed_rate)}
        if axis in ['x', 'X']:
            kwargs['x'] = int(step)
        elif axis in ['y', 'Y']:
            kwargs['y'] = int(step)
        elif axis in ['z', 'Z']:
            kwargs['z'] = int(step)
        self._execute_cnc_command(uid, 'move_by', **kwargs)
    
    def move_relative(self, uid, x=None, y=None, z=None, feed_rate=None):
        """Move CNC by relative amounts on multiple axes simultaneously"""
        kwargs = {}
        if feed_rate is not None:
            kwargs['feed_rate'] = int(feed_rate)
        if x is not None and x != 0:
            kwargs['x'] = round(float(x), 3)
        if y is not None and y != 0:
            kwargs['y'] = round(float(y), 3)
        if z is not None and z != 0:
            kwargs['z'] = round(float(z), 3)
        
        # Only execute if at least one axis has movement
        if any(k in kwargs for k in ['x', 'y', 'z']):
            self._execute_cnc_command(uid, 'move_by', **kwargs)

    async def move_to_location(self, uid, location: LocationModel, block, timeout):
        await self._execute_cnc_command(uid, 'move_to_location_j', location=location, block=block, timeout=timeout)

    def get_cnc_info(self, uid):
        """Get information about a CNC including connection status"""
        if uid not in self._cnc_objects:
            return {'exists': False, 'is_mock': False, 'connection_error': 'CNC not found'}
        
        cnc_obj = self._cnc_objects[uid]
        is_mock = isinstance(cnc_obj, Mock)
        connection_error = self._connection_errors.get(uid, 'No error') if is_mock else None
        
        try:
            cnc_data = self._cnc_repo.read_id(uid)
            cnc_name = cnc_data.get('name', 'Unknown')
            cnc_port = cnc_data.get('port', 'Unknown')
            cnc_type = cnc_data.get('type', 'Unknown')
        except Exception:
            cnc_name = 'Unknown'
            cnc_port = 'Unknown'
            cnc_type = 'Unknown'
        
        return {
            'exists': True,
            'is_mock': is_mock,
            'connection_error': connection_error,
            'name': cnc_name,
            'port': cnc_port,
            'type': cnc_type,
            'uid': uid
        }