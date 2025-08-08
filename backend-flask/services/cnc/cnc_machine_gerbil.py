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

ERROR_LIST_CNC = {
        "error:1": "G - code words consist of a letter and a value. Letter was not found.",
        "error:2": "Numeric value format is not valid or missing an expected value.",
        "error:3": "Grbl ‘$’ system command was not recognized or supported.",
        "error:4": "Negative value received for an expected positive value.",
        "error:5": "Homing cycle is not enabled via settings.",
        "error:6": "Minimum step pulse time must be greater than 3usec",
        "error:7": "EEPROM read failed.Reset and restored to default values.",
        "error:8": "Grbl ‘$’ command cannot be used unless Grbl is IDLE.Ensures smooth operation during a job.",
        "error:9": "G - code locked out during alarm or jog state",
        "error:10": "Soft limits cannot be enabled without homing also enabled.",
        "error:11": "Max characters per line exceeded.Line was not processed and executed.",
        "error:12": "(Compile Option) Grbl ‘$’ setting value exceeds the maximum step rate supported.",
        "error:13": "Safety door detected as opened and door state initiated.",
        "error:14": "(Grbl - Mega Only) Build info or startup line exceeded EEPROM line length limit.",
        "error:15": "Jog target exceeds machine travel.Command ignored.",
        "error:16": "Jog command with no ‘=’ or contains prohibited g-code.",
        "error:20": "Unsupported or invalid g - code command found in block.",
        "error:21": "More than one g - code command from same modal group found in block.",
        "error:22": "Feed rate has not yet been set or is undefined.",
        "error:23": "G - code command in block requires an integer value.",
        "error:24": "Two G - code commands that both require the use of the XYZ axis words were detected in the block.",
        "error:25": "A G - code word was repeated in the block.",
        "error:26": "A G - code command implicitly or explicitly requires XYZ axis words in the block, but none were detected.",
        "error:27": "N line number value is not within the valid range of 1 – 9, 999, 999.",
        "error:28": "A G - code command was sent, but is missing some required P or L value words in the line.",
        "error:29": "Grbl supports six work coordinate systems G54 - G59.G59.1, G59.2, and G59.3 are not supported.",
        "error:30": "The G53 G - code command requires either a G0 seek or G1 feed motion mode to be active.A different motion was active.",
        "error:31": "There are unused axis words in the block and G80 motion mode cancel is active.",
        "error:32": "A G2 or G3 arc was commanded, but there are no XYZ axis words in the selected plane to trace the arc.",
        "error:33": "The motion command has an invalid target.G2, G3, and G38.2 generates this error, if the arc is impossible to generate or if the probe target is the current position.",
        "error:34": "A G2 or G3 arc, traced with the radius definition, had a mathematical error when computing the arc geometry.Try either breaking up the arc into semi-circles or quadrants, or redefine them with the arc offset definition.",
        "error:35": "A G2 or G3 arc, traced with the offset definition, is missing the IJK offset word in the selected plane to trace the arc.",
        "error:36": "There are unused, leftover G - code words that aren’t used by any command in the block.",
        "error:37": "The G43.1 dynamic tool length offset command cannot apply an offset to an axis other than its configured axis. The Grbl default axis is the Z - axis.",
        "error:38": "An invalid tool number sent to the parser",
        "ALARM:1": "Hard limit triggered.Machine position is likely lost due to sudden and immediate halt.Re - homing is highly recommended.",
        "ALARM:2": "G - code motion target exceeds machine travel.Machine position safely retained.Alarm may be unlocked.",
        "ALARM:3": "Reset while in motion.Grbl cannot guarantee position.Lost steps are likely.Re-homing is highly recommended.",
        "ALARM:4": "Probe fail.The probe is not in the expected initial state before starting probe cycle, where G38.2 and G38.3 is not "
                   "triggered and G38.4 and G38.5 is triggered.",
        "ALARM:5": "Probe fail.Probe did not contact the workpiece within the programmed travel for G38.2 and G38.4.",
        "ALARM:6": "Homing fail.Reset during active homing cycle.",
        "ALARM:7": "Homing fail.Safety door was opened during active homing cycle.",
        "ALARM:8": "Homing fail.Cycle failed to clear limit switch when pulling off.Try increasing pull - off setting or check wiring.",
        "ALARM:9": "Homing fail.Could not find limit switch within search distance.Defined as 1.5 * max_travel on search and 5 * pulloff on locate phases.",
        "Hold:0": "Hold complete.Ready to resume.",
        "Hold:1": "Hold in -progress.Reset will throw an alarm.",
        "Door:0": "Door closed.Ready to resume.",
        "Door:1": "Machine stopped.Door still ajar.Can’t resume until closed.",
        "Door:2": "Door opened.Hold( or parking retract) in -progress.Reset will throw an alarm.",
        "Door:3": "Door closed and resuming.Restoring from park, if applicable.Reset will throw an alarm.",
        "error: Bad number format": "Bad number format",
        "'ALARM: Abort during cycle'": 'ALARM: Abort during cycle'
    }
INSTRUCTIONS = {
        "$0": "(Step pulse time, microseconds)",
        "$1": "(Step idle delay, milliseconds)",
        "$2": "(Step pulse invert, mask)",
        "$3": "(Step direction invert, mask)",
        "$4": "(Invert step enable  pin, boolean)",
        "$5": "(Invert limit pins, boolean)",
        "$6": "(Invert probe pin, boolean)",
        "$10": "(Status report options, mask)",
        "$11": "(Junction deviation, millimeters)",
        "$12": "(Arc tolerance, millimeters)",
        "$13": "(Report in inches, boolean)",
        "$20": "(Soft limits enable, boolean)",
        "$21": "(Hard limits enable, boolean)",
        "$22": "(Homing cycle enable, boolean)",
        "$23": "(Homing direction invert, mask)",
        "$24": "(Homing locate feed rate, mm / min)",
        "$25": "(Homing search seek rate, mm / min)",
        "$26": "(Homing switch debounce delay, milliseconds)",
        "$27": "(Homing switch pull - off  distance, millimeters)",
        "$30": "(Maximum spindle speed, RPM)",
        "$31": "(Minimum spindle speed, RPM)",
        "$32": "(Laser - mode enable, boolean)",
        "$100": "(X - axis travel resolution, step / mm)",
        "$101": "(Y - axis travel resolution, step / mm)",
        "$102": "(Z - axis travel resolution, step / mm)",
        "$110": "(X - axis maximum rate, mm / min)",
        "$111": "(Y - axis maximum rate, mm / min)",
        "$112": "(Z - axis maximum rate, mm / min)",
        "$120": "(X - axis acceleration, mm / sec ^ 2)",
        "$121": "(Y - axis acceleration, mm / sec ^ 2)",
        "$122": "(Z - axis acceleration, mm / sec ^ 2)",
        "$130": "(X - axis maximum travel, millimeters)",
        "$131": "(Y - axis maximum travel, millimeters)",
        "$132": "(Z - axis maximum travel, millimeters)"
    }


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
            return LocationModel(uid=None, axis_uid=None, degree_in_step=None, feedrate=None, name=None, x=pos_tuple[0], y=pos_tuple[1], z=pos_tuple[2])
        return None

    def get_instruction(self, data):
        try:
            key = data.split("=")[0]
            value = data.split("=")[1]
            return key, value, self.INSTRUCTIONS[key]
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
        if self._gerbil:
            try:
                self._gerbil.soft_reset()
                self._gerbil.disconnect()
                # Clean up reference to allow reconnection
                self._gerbil = None
            except Exception as e:
                # Still clean up even if disconnect fails
                self._gerbil = None
                raise e