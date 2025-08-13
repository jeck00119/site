import time
from asyncio import sleep
from enum import Enum

from services.cnc.cnc_models import LocationModel
from services.cnc.dependencies.marlin.marlin import Marlin
from services.cnc.base_cnc_machine import BaseCncMachine


class MarlinStates(Enum):
    IDLE = 'Idle'
    JOG = 'Jog'
    ALARM = 'Error'
    HOME = "G28\n"


# Import error list from centralized handler
from services.cnc.cnc_error_handler import CncErrorHandler
ERROR_LIST_CNC = CncErrorHandler.MARLIN_ERROR_LIST


class CncMachineMarlin(BaseCncMachine):
    def __init__(self, port: str, cnc_name, callback=()):
        super().__init__()
        self._port = port
        self.callback = callback
        self._marlin = None
        self._marlin_state = None

        self.ui_cnc_event = lambda: print

    def init(self):
        try:
            self._marlin: Marlin = Marlin(self.callback)
            self._marlin.connect(self._port)
            # Wait longer for connection and protocol sync to stabilize
            time.sleep(2) 
            # Enable steppers after connection so motors can move
            self.tension_on()
        except Exception as e:
            raise e

    # Inherited from BaseCncMachine:
    # - get_port()
    # - _is_at()
    # - is_at() 
    # - is_at_location()

    def send(self, command: str):
        if self._marlin:
            try:
                print(f"Command inside Marlin object: {command}")
                self._marlin.stream(command)
            except Exception as e:
                raise e

    def tension_on(self):
        self.send("M17")

    def tension_off(self):
        self.send("M18")

    def request_settings(self):
        if self._marlin:
            try:
                self._marlin.request_settings()
            except Exception as e:
                raise e

    def zero_pos(self):
        return self._marlin.current_position if self._marlin else None

    def current_pos(self):
        if self._marlin:
            pos_tuple = self._marlin.current_position
            return self.create_location_model(pos_tuple)
        return None

    def get_instruction(self, data):
        try:
            key = data.split("=")[0]
            value = data.split("=")[1]
            instruction = self._marlin.INSTRUCTIONS.get(key, '')
            return key, value, instruction
        except Exception as e:
            return '', '', ''

    # parse_coordinates() inherited from BaseCncMachine

    def state(self):
        if self._marlin:
            return self._marlin.current_mode
        return None

    async def move_to_location_j(self, location: LocationModel, block=False, timeout=10, callback_loc=None,
                                 callback=None):
        try:
            if callback_loc is not None and callback is not None:
                use_callback = True
                called = False
            else:
                use_callback = False
            if self._marlin:
                self._marlin.stream(
                    f"G90 G1 {self.parse_coordinates(location.x, location.y, location.z, location.feedrate)}")
                if block:
                    t1 = time.time()
                    if use_callback:
                        while True:
                            if self._abort_requested:
                                self._abort_requested = False
                                break

                            if self.is_at_location(callback_loc) and not called:
                                callback()
                                called = True
                            if self.is_at_location(location) or time.time() - t1 > (timeout * 1):
                                break
                            await sleep(0.01)
                    else:
                        while True:
                            if self._abort_requested:
                                self._abort_requested = False
                                break

                            if self.is_at_location(location) or time.time() - t1 > (timeout * 1):
                                break
                            await sleep(0.01)
        except Exception as e:
            self._abort_requested = False
            raise e

    def move_by(self, x: float = None, y: float = None, z: float = None, feed_rate: int = None):
        if self._marlin:
            try:
                # Use proper Marlin protocol with line numbering and checksums
                print(f"[MOVE_BY DEBUG] Using proper Marlin protocol")
                print(f"[MOVE_BY DEBUG] Params: X={x} Y={y} Z={z} F={feed_rate}")
                
                # Immediately set state to Jog when starting movement
                if self._marlin.current_mode != "Jog":
                    self._marlin.current_mode = "Jog"
                    self.callback("on_stateupdate", "Jog", self._marlin.current_position, 
                                  self._marlin.current_work_position)
                
                # Use stream method to ensure proper line numbering and checksums
                # Send G91 first as separate command
                self._marlin.stream("G91")
                
                # Use G1 (linear interpolation) to properly respect feedrate
                command = f"G1 {self.parse_coordinates(x, y, z, feed_rate)}"
                print(f"[MOVE_BY DEBUG] Movement command: {command}")
                self._marlin.stream(command)
                
                # Return to absolute mode
                self._marlin.stream("G90")
                
            except Exception as e:
                raise e
                

    def abort(self):
        if self._marlin:
            try:
                self._abort_requested = True
                self._marlin.abort()
            except Exception as e:
                self._abort_requested = False
                raise e

    async def home(self, block=False, timeout=10):
        if self._marlin:
            self._marlin.home()
            if block:
                t1 = time.time()
                while self._marlin.is_homing and time.time() - t1 < timeout:
                    if self._abort_requested:
                        self._abort_requested = False
                        break
                    await sleep(0.1)

    def unlock(self):
        if self._marlin:
            try:
                self._marlin.stream("M999")
            except Exception as e:
                raise e

    def soft_reset(self):
        if self._marlin:
            try:
                self._abort_requested = False
                self._marlin.soft_reset()
            except Exception as e:
                raise e

    def zero_reset(self):
        if self._marlin:
            try:
                self._marlin.stream("G92 X0 Y0 Z0")
            except Exception as e:
                raise e

    def return_to_zero(self):
        if self._marlin:
            try:
                self._marlin.stream("G90 G0 X0 Y0")
                self._marlin.stream("G90 G0 Z0")
            except Exception as e:
                raise e

    def disconnect(self):
        self.standard_disconnect_cleanup('_marlin')