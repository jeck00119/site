import time
from asyncio import sleep
from enum import Enum

from services.cnc.cnc_models import LocationModel
from services.cnc.dependencies.marlin.marlin import Marlin


class MarlinStates(Enum):
    IDLE = 'Idle'
    JOG = 'Jog'
    ALARM = 'Error'
    HOME = "G28\n"


ERROR_LIST_CNC = {
    "Error:1": "Temperature is below target temperature",
    "Error:2": "Temperature is above target temperature",
    "Error:3": "MAXTEMP triggered",
    "Error:4": "MINTEMP triggered",
    "Error:5": "MAXTEMP_BED triggered",
    "Error:6": "MINTEMP_BED triggered",
    "Error:7": "Homing failed",
    "Error:8": "Probing failed",
    "Error:9": "Max travel exceeded",
    "Error:10": "Printer halted. kill() called!",
    "Error:11": "Failed to enable stepper motors",
    "Error:12": "Unknown command",
    "Error:13": "Invalid parameter",
    "Error:14": "Command buffer overflow",
    "Error:15": "Stepper driver error",
    "Error:20": "Invalid G-code command"
}


class CncMachineMarlin():
    def __init__(self, port: str, cnc_name, callback=()):
        super().__init__()
        self._port = port
        self.callback = callback
        self._marlin = None
        self._marlin_state = None
        self._abort_requested = False

        self.ui_cnc_event = lambda: print

    def init(self):
        try:
            self._marlin: Marlin = Marlin(self.callback)
            self._marlin.connect(self._port)
        except Exception as e:
            raise e

    def get_port(self):
        return self._port

    @staticmethod
    def _is_at(x, current_x):
        if x is None:
            return True
        else:
            return abs(x) == abs(current_x)

    def is_at(self, x, y, z):
        pos = self.current_pos()
        if not pos:
            return False
        return self._is_at(x, pos.x) \
            and self._is_at(y, pos.y) \
            and self._is_at(z, pos.z)

    def is_at_location(self, location: LocationModel):
        x = location.x
        y = location.y
        z = location.z
        return self.is_at(x, y, z)

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
            return LocationModel(uid=None, axis_uid=None, degree_in_step=None, feedrate=None, name=None, x=pos_tuple[0],
                                 y=pos_tuple[1], z=pos_tuple[2])
        return None

    def get_instruction(self, data):
        try:
            key = data.split("=")[0]
            value = data.split("=")[1]
            instruction = self._marlin.INSTRUCTIONS.get(key, '')
            return key, value, instruction
        except Exception as e:
            return '', '', ''

    def parse_coordinates(self, x, y, z, feed_rate):
        line = ""
        if x is not None:
            line += f"X{x}"
        if y is not None:
            line += f"Y{y}"
        if z is not None:
            line += f"Z{z}"
        if feed_rate is not None:
            line += f"F{int(feed_rate)}"
        return line

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
                self._marlin.stream(f"G91 G1 {self.parse_coordinates(x, y, z, feed_rate)}")
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
        if self._marlin:
            try:
                self._abort_requested = False
                self._marlin.soft_reset()
                self._marlin.disconnect()
            except Exception as e:
                raise e