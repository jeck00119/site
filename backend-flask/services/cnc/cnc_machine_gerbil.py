import time
from asyncio import sleep
from enum import Enum

from services.cnc.cnc_models import LocationModel
from services.cnc.dependencies.gerbil.gerbil import Gerbil
from services.cnc.base_cnc_machine import BaseCncMachine


class GrblStates(Enum):
    IDLE = 'Idle'
    JOG = 'Jog'
    ALARM = 'Alarm'
    HOME = "$H\n"

# Import error list and instructions from centralized handler
from services.cnc.cnc_error_handler import CncErrorHandler
ERROR_LIST_CNC = CncErrorHandler.GRBL_ERROR_LIST
INSTRUCTIONS = CncErrorHandler.GRBL_INSTRUCTIONS


class CncMachineGerbil(BaseCncMachine):
    def __init__(self, port: str, cnc_name,  callback=()):
        super().__init__()
        self._port = port
        self.callback = callback
        self._gerbil = None
        self._grbl_state = None
        self.ui_cnc_event = lambda: print

    def init(self):
        try:
            self._gerbil: Gerbil = Gerbil(self.callback)
            self._gerbil.cnect(self._port)
            # Enable steppers after connection so motors can move
            time.sleep(1)  # Wait for connection to stabilize
            self.tension_on()
        except Exception as e:
            raise e

    # Inherited from BaseCncMachine:
    # - get_port()
    # - _is_at()
    # - is_at() 
    # - is_at_location()

    def send(self, command: str):
        if self._gerbil:
            try:
                self._gerbil.stream(command)
            except Exception as e:
                raise e

    def tension_on(self):
        self.send("$1=255")

    def tension_off(self):
        self.send("$1=55")

    def request_settings(self):
        if self._gerbil:
            try:
                self._gerbil.request_settings()
            except Exception as e:
                raise e

    def zero_pos(self):
        return self._gerbil.cwpos if self._gerbil else None

    def current_pos(self):
        if self._gerbil:
            pos_tuple = self._gerbil.cwpos
            return self.create_location_model(pos_tuple)
        return None

    def get_instruction(self, data):
        try:
            key = data.split("=")[0]
            value = data.split("=")[1]
            return key, value, INSTRUCTIONS[key]
        except Exception as e:
            return '','',''

    # parse_coordinates() inherited from BaseCncMachine

    def state(self):
        if self._gerbil:
            return self._gerbil.cmode
        return None

    async def move_to_location_j(self, location: LocationModel, block=False, timeout=10, callback_loc=None, callback=None):
        try:
            if callback_loc is not None and callback is not None:
                use_callback = True
                called = False
            else:
                use_callback = False
            if self._gerbil:
                self._gerbil.stream(
                    f"$J=G90{self.parse_coordinates(location.x, location.y, location.z, location.feedrate)}")
                if block:
                    t1 = time.time()
                    if use_callback:
                        while True:
                            if self.is_at_location(callback_loc) and not called:
                                callback()
                                called = True
                            if self.is_at_location(location) or time.time() - t1 > (timeout * 1):
                                break
                            await sleep(0.01)
                    else:
                        pass
        except Exception as e:
            raise e

    def move_by(self, x: float = None, y: float = None, z: float = None, feed_rate: int = None):
        if self._gerbil:
            try:
                self._gerbil.stream(f"$J=G91{self.parse_coordinates(x, y, z, feed_rate)}")
            except Exception as e:
                raise e

    def abort(self):
        if self._gerbil:
            try:
                self._gerbil.abort()
            except Exception as e:
                raise e

    async def home(self, block=False, timeout=10):
        self._gerbil.homing()

    def unlock(self):
        if self._gerbil:
            try:
                self._gerbil.killalarm()
            except Exception as e:
                raise e

    def soft_reset(self):
        if self._gerbil:
            try:
                self._gerbil.soft_reset()
            except Exception as e:
                raise e

    def zero_reset(self):
        if self._gerbil:
            try:
                self._gerbil.stream("G10 L20 P0 X0 Y0 Z0")
            except Exception as e:
                raise e

    def return_to_zero(self):
        if self._gerbil:
            try:
                self._gerbil.stream("G90 G0 X0 Y0")
                self._gerbil.stream("G90 G0 Z0")
            except Exception as e:
                raise e

    def disconnect(self):
        self.standard_disconnect_cleanup('_gerbil')