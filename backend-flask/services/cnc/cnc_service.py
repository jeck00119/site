from collections import deque
from typing import Union
from unittest.mock import Mock
import time

from serial import SerialException

from repo.repositories import CncRepository, LocationRepository
from services.cnc.cnc_machine_gerbil import CncMachineGerbil, ERROR_LIST_CNC as GRBL_ERROR_LIST
from services.cnc.cnc_machine_marlin import CncMachineMarlin, ERROR_LIST_CNC as MARLIN_ERROR_LIST
from services.cnc.cnc_models import CncModel, LocationModel
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
        self._error_lists = {
            "GRBL": GRBL_ERROR_LIST,
            "FluidNC": GRBL_ERROR_LIST,
            "Marlin": MARLIN_ERROR_LIST
        }
        self.logger = logging.getLogger(__name__)
        
        # Message batching configuration
        self._batch_buffers: dict[str, list] = {}
        self._last_batch_time: dict[str, float] = {}
        self._batch_interval = 0.05  # 50ms batching interval
        self._max_batch_size = 10    # Maximum messages per batch

    @staticmethod
    def get_available_types():
        return ["GRBL", "FluidNC", "Marlin"]

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
        current_cnc_repo = CncRepository()
        for cnc in current_cnc_repo.read_all():
            try:
                if cnc['uid'] not in self._callbacks_buffers:
                    self._callbacks_buffers[cnc['uid']] = deque(maxlen=20)
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
            buffed = self._callbacks_buffers[uid].popleft()[0]
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
            error_list = self._error_lists.get(cnc_type, GRBL_ERROR_LIST)
            error_message = error_list.get(buffed[1], buffed[1])
            return {'event': event, "message": error_message}

        elif event in ["on_job_completed", "on_movement", "on_standstill", "on_boot", "on_write", "on_feed_change"]:
            return {'event': event}

        else:
            message = str(buffed[1:]) if len(buffed) > 1 else ''
            return {'event': event, 'message': message}
    
    def _has_priority_message(self, messages):
        """Check if batch contains priority messages that should be sent immediately"""
        priority_events = ["on_error", "on_alarm", "on_job_completed", "on_boot"]
        return any(msg.get('event') in priority_events for msg in messages)

    def _get_cnc_type(self, uid):
        try:
            cnc = self._cnc_repo.read_id(uid)
            return cnc.get('type', 'GRBL')
        except Exception:
            return 'GRBL'

    def update_cncs(self, cnc_models: list):
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
                if cnc_model.port != self._cnc_objects.get(cnc_model.uid, Mock()).get_port():
                    self._deinit_cnc(cnc_model.uid)
                    self._init_cnc_from_model(cnc_model)
                    update.append(cnc_model.uid)
            else:
                self._init_cnc_from_model(cnc_model)
                add.append(cnc_model.uid)
        for axis_uid, found in found_axis.items():
            if not found:
                self._deinit_cnc(axis_uid)
                delete.append(axis_uid)
        return add, update, delete

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
        self._cnc_objects[cnc_model.uid].init()

    def _init_cnc(self, uid):
        if uid not in self._cnc_objects.keys():
            current_cnc_repo = CncRepository()
            doc = current_cnc_repo.read_id(uid)
            cnc_model: CncModel = CncModel(**doc)
            try:
                self._init_cnc_from_model(cnc_model)
            except SerialException as e:
                error_msg = f"Serial connection failed: {e}"
                self.logger.error(f"CNC {uid}: {error_msg}")
                self._connection_errors[uid] = error_msg
                self._cnc_objects[uid] = Mock()
            except Exception as e:
                error_msg = f"Initialization failed: {e}"
                self.logger.error(f"CNC {uid}: {error_msg}")
                self._connection_errors[uid] = error_msg
                self._cnc_objects[uid] = Mock()

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

    def update_cnc(self, cnc_uid):
        self._deinit_cnc(cnc_uid)
        self._init_cnc(cnc_uid)

    def delete_cnc(self, cnc_uid):
        self._deinit_cnc(cnc_uid)

    def abort(self, uid):
        try:
            if uid in self._cnc_objects:
                cnc_obj = self._cnc_objects[uid]
                if isinstance(cnc_obj, Mock):
                    raise Exception(f"CNC {uid} is not connected (Mock object). Connection error: {self._connection_errors.get(uid, 'Unknown connection error')}")
                if hasattr(cnc_obj, '_abort_requested'):
                    cnc_obj._abort_requested = True
                cnc_obj.abort()
        except Exception as e:
            error_msg = f"Error during abort on CNC {uid}: {str(e)}"
            self.logger.error(error_msg)
            self._exceptions.append(error_msg)
            raise e

    async def home(self, uid):
        if uid in self._cnc_objects:
            cnc_obj = self._cnc_objects[uid]
            if isinstance(cnc_obj, Mock):
                raise Exception(f"CNC {uid} is not connected (Mock object). Connection error: {self._connection_errors.get(uid, 'Unknown connection error')}")
            await cnc_obj.home()

    def soft_reset(self, uid):
        if uid in self._cnc_objects:
            cnc_obj = self._cnc_objects[uid]
            if isinstance(cnc_obj, Mock):
                raise Exception(f"CNC {uid} is not connected (Mock object). Connection error: {self._connection_errors.get(uid, 'Unknown connection error')}")
            cnc_obj.soft_reset()

    def zero_reset(self, uid):
        if uid in self._cnc_objects:
            cnc_obj = self._cnc_objects[uid]
            if isinstance(cnc_obj, Mock):
                raise Exception(f"CNC {uid} is not connected (Mock object). Connection error: {self._connection_errors.get(uid, 'Unknown connection error')}")
            cnc_obj.zero_reset()

    def return_to_zero(self, uid):
        if uid in self._cnc_objects:
            cnc_obj = self._cnc_objects[uid]
            if isinstance(cnc_obj, Mock):
                raise Exception(f"CNC {uid} is not connected (Mock object). Connection error: {self._connection_errors.get(uid, 'Unknown connection error')}")
            cnc_obj.return_to_zero()

    def unlock(self, uid):
        if uid in self._cnc_objects:
            cnc_obj = self._cnc_objects[uid]
            if isinstance(cnc_obj, Mock):
                raise Exception(f"CNC {uid} is not connected (Mock object). Connection error: {self._connection_errors.get(uid, 'Unknown connection error')}")
            cnc_obj.unlock()

    def send(self, uid, command):
        if uid in self._cnc_objects:
            cnc_obj = self._cnc_objects[uid]
            if isinstance(cnc_obj, Mock):
                raise Exception(f"CNC {uid} is not connected (Mock object). Connection error: {self._connection_errors.get(uid, 'Unknown connection error')}")
            self.logger.debug(f"Received command service: {command}")
            cnc_obj.send(command)

    def axis_minus(self, uid, axis, step, feed_rate):
        if uid in self._cnc_objects:
            cnc_obj = self._cnc_objects[uid]
            if isinstance(cnc_obj, Mock):
                raise Exception(f"CNC {uid} is not connected (Mock object). Connection error: {self._connection_errors.get(uid, 'Unknown connection error')}")
            if axis in ['x', 'X']:
                cnc_obj.move_by(x=-int(step), feed_rate=int(feed_rate))
            if axis in ['y', 'Y']:
                cnc_obj.move_by(y=-int(step), feed_rate=int(feed_rate))
            if axis in ['z', 'Z']:
                cnc_obj.move_by(z=-int(step), feed_rate=int(feed_rate))

    def axis_plus(self, uid, axis, step, feed_rate):
        if uid in self._cnc_objects:
            cnc_obj = self._cnc_objects[uid]
            if isinstance(cnc_obj, Mock):
                raise Exception(f"CNC {uid} is not connected (Mock object). Connection error: {self._connection_errors.get(uid, 'Unknown connection error')}")
            if axis in ['x', 'X']:
                cnc_obj.move_by(x=int(step), feed_rate=int(feed_rate))
            if axis in ['y', 'Y']:
                cnc_obj.move_by(y=int(step), feed_rate=int(feed_rate))
            if axis in ['z', 'Z']:
                cnc_obj.move_by(z=int(step), feed_rate=int(feed_rate))

    async def move_to_location(self, uid, location: LocationModel, block, timeout):
        if uid in self._cnc_objects:
            cnc_obj = self._cnc_objects[uid]
            if isinstance(cnc_obj, Mock):
                raise Exception(f"CNC {uid} is not connected (Mock object). Connection error: {self._connection_errors.get(uid, 'Unknown connection error')}")
            await cnc_obj.move_to_location_j(location=location, block=block, timeout=timeout)

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