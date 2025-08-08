import atexit
import logging
import re
import threading
import time
import traceback
from queue import Queue

from services.cnc.dependencies.gerbil.callbackloghandler import CallbackLogHandler
from services.cnc.dependencies.gerbil.gcode_machine import GcodeMachine
from services.cnc.dependencies.gerbil.interface import Interface


class MarlinBufferManager:
    """Centralized buffer management for Marlin protocol"""
    
    @staticmethod
    def clear_all_buffers(marlin_instance):
        """Clear all Marlin buffers to reset communication state"""
        marlin_instance.buffer.clear()
        marlin_instance.buffer_size = 0
        marlin_instance._rx_buffer_fill.clear()
        marlin_instance._rx_buffer_backlog.clear()
        marlin_instance._rx_buffer_backlog_line_number.clear()
        # Reset active command counter when clearing buffers
        marlin_instance._active_command_count = 0

    @staticmethod  
    def reset_line_sync(marlin_instance, expected_line: int):
        """Reset line synchronization and clear buffers"""
        marlin_instance.logger.warning(f"SYNC FIX: Setting line number to {expected_line}, was {marlin_instance._line_number}")
        marlin_instance._line_number = expected_line
        MarlinBufferManager.clear_all_buffers(marlin_instance)
        # Reset resend tracking
        marlin_instance._last_resend = None
        marlin_instance._resend_count = 0
        # Stop any current streaming to prevent further line number conflicts
        marlin_instance._streaming_enabled = False
        marlin_instance._set_streaming_complete(True)


class MarlinCommandVerifier:
    """Centralized command verification and retry logic"""
    
    @staticmethod
    def detect_command_corruption(line: str) -> tuple[bool, str]:
        """Detect if a command was corrupted and identify the original command"""
        if "Unknown command:" not in line:
            return False, ""
            
        # Extract the corrupted command
        import re
        match = re.search(r'Unknown command: "([^"]+)"', line)
        if not match:
            return False, ""
            
        corrupted_cmd = match.group(1)
        
        # Common corruption patterns
        corruption_fixes = {
            'MM110': 'M110',
            'MM114': 'M114', 
            'MM17': 'M17',
            'MM18': 'M18',
            'MM999': 'M999',
            'GG28': 'G28',
            'GG90': 'G90',
            'GG91': 'G91',
        }
        
        for corrupted, original in corruption_fixes.items():
            if corrupted in corrupted_cmd:
                return True, corrupted_cmd.replace(corrupted, original)
                
        return True, ""  # Detected corruption but couldn't fix
    
    @staticmethod
    def should_retry_command(marlin_instance, original_cmd: str) -> bool:
        """Determine if a corrupted command should be automatically retried"""
        # Don't retry if we're in an error state or have too many active commands
        if marlin_instance.current_mode == "Error":
            return False
        if marlin_instance._active_command_count > 5:  # Prevent buffer overflow
            return False
        
        # Only retry simple commands automatically
        safe_retry_commands = ['M110', 'M114', 'M17', 'M18', 'M999']
        return any(original_cmd.startswith(cmd) for cmd in safe_retry_commands)


class MarlinErrorHandler:
    """Centralized error handling for Marlin protocol"""
    
    @staticmethod
    def handle_line_number_error(marlin_instance, line: str, logger) -> bool:
        """Handle line number mismatch errors. Returns True if handled."""
        if "Line Number is not Last Line Number+1" not in line:
            return False
            
        # Extract the expected line number from error message  
        import re
        match = re.search(r'Last Line: (\d+)', line)
        if match:
            expected_line = int(match.group(1)) + 1
            logger.warning(f"FORCE SYNC: Resetting line number from {marlin_instance._line_number} to {expected_line}")
            MarlinBufferManager.reset_line_sync(marlin_instance, expected_line)
        return True
    
    @staticmethod
    def handle_checksum_error(marlin_instance, line: str, logger) -> bool:
        """Handle checksum mismatch errors. Returns True if handled."""
        if "checksum mismatch" not in line:
            return False
            
        import re
        match = re.search(r'Last Line: (\d+)', line)
        if match:
            expected_line = int(match.group(1)) + 1
            logger.warning(f"Checksum error - resetting line number from {marlin_instance._line_number} to {expected_line}")
            MarlinBufferManager.reset_line_sync(marlin_instance, expected_line)
        return True
    
    @staticmethod
    def handle_resend_request(marlin_instance, line: str, logger) -> bool:
        """Handle resend requests. Returns True if handled."""
        if not line.startswith("Resend:"):
            return False
            
        import re
        match = re.search(r'Resend: (\d+)', line)
        if match:
            resend_line = int(match.group(1))
            
            # Check for infinite resend loop
            if marlin_instance._last_resend == resend_line:
                marlin_instance._resend_count += 1
                if marlin_instance._resend_count > 5:
                    logger.error(f"RESEND LOOP DETECTED: Ignoring repeated resend request for line {resend_line}")
                    # Force a hard reset to break the loop
                    marlin_instance._line_number = resend_line
                    marlin_instance._resend_count = 0
                    marlin_instance._last_resend = None
                    marlin_instance._streaming_enabled = False
                    return True
            else:
                marlin_instance._resend_count = 1
                marlin_instance._last_resend = resend_line
            
            logger.warning(f"RESEND: Syncing line number from {marlin_instance._line_number} to {resend_line} (attempt {marlin_instance._resend_count})")
            MarlinBufferManager.reset_line_sync(marlin_instance, resend_line)
        return True


class Marlin:
    def __init__(self, callback):
        self.name = "marlin"
        self.current_mode = "Idle"
        self.current_position = (0, 0, 0)
        self.current_work_position = (0, 0, 0)
        self.gps = [
            "0",
            "54",
            "17",
            "21",
            "90",
            "94",
            "0",
            "0",
            "5",
            "0",
            "99",
            "0",
        ]
        # Reduced polling interval for faster position updates during movement
        # Was 0.2 (200ms), now 0.05 (50ms) for real-time tracking
        self.poll_interval = 0.05
        self.settings = {}
        self.settings_hash = {
            "G54": (0, 0, 0),
            "G55": (0, 0, 0),
            "G56": (0, 0, 0),
            "G57": (0, 0, 0),
            "G58": (0, 0, 0),
            "G59": (0, 0, 0),
            "G28": (0, 0, 0),
            "G30": (0, 0, 0),
            "G92": (0, 0, 0),
            "TLO": 0,
            "PRB": (0, 0, 0),
        }
        self.gcode_parser_state_requested = False
        self.hash_state_requested = False
        self.logger = logging.getLogger("marlin")
        self.logger.setLevel(5)
        self.logger.propagate = False
        self.target = "firmware"
        self.connected = False
        self.initialized = False
        self.preprocessor = GcodeMachine()
        self.preprocessor.callback = self._preprocessor_callback
        self.travel_dist_buffer = {}
        self.travel_dist_current = {}
        self.is_standstill = False
        self.is_homing = False
        self._ifacepath = None
        self._last_mode = None
        self._last_position = (0, 0, 0)
        self._last_work_position = (0, 0, 0)
        self._rx_buffer_size = 128
        self._rx_buffer_fill = []
        self._rx_buffer_backlog = []
        self._rx_buffer_backlog_line_number = []
        self._rx_buffer_fill_percent = 0
        self._current_line = ""
        self._current_line_sent = True
        self._streaming_mode = None
        self._wait_empty_buffer = False
        self.streaming_complete = True
        self.job_finished = True
        self._streaming_src_end_reached = True
        self._streaming_enabled = False  # Start with polling enabled for idle machine
        self._error = False
        self._incremental_streaming = False
        self.buffer = []
        self.buffer_size = 0
        self._current_line_nr = 0
        self.buffer_stash = []
        self.buffer_size_stash = 0
        self._current_line_nr_stash = 0
        self._line_number = 1  # Marlin line numbering starts at 1
        self._last_resend = None  # Track last resend request to prevent loops
        self._resend_count = 0    # Count consecutive resends
        self._command_delay = 0.02  # 20ms delay between commands for responsive control
        self._active_command_count = 0  # Track active numbered commands
        self._poll_keep_alive = False
        self._iface_read_do = False
        self._thread_polling = None
        self._thread_read_iface = None
        self._iface = None
        self._queue = Queue()
        self._loghandler = None
        self.callback = callback
        self.INSTRUCTIONS = {
            "$0": "(Steps per unit X)",
            "$1": "(Steps per unit Y)",
            "$2": "(Steps per unit Z)",
            "$3": "(Steps per unit E)",
            "$4": "(Max feedrate X)",
            "$5": "(Max feedrate Y)",
            "$6": "(Max feedrate Z)",
            "$7": "(Max feedrate E)",
            "$8": "(Acceleration X)",
            "$9": "(Acceleration Y)",
            "$10": "(Acceleration Z)",
            "$11": "(Acceleration E)",
            "$12": "(Junction Deviation)",
            "$13": "(Print/Travel acceleration)",
            "$20": "(Min feedrate)",
            "$21": "(Min travel feedrate)",
            "$22": "(Min segment time)",
            "$30": "(Max X position)",
            "$31": "(Max Y position)",
            "$32": "(Max Z position)",
            "$100": "(X home dir)",
            "$101": "(Y home dir)",
            "$102": "(Z home dir)",
            "$130": "(Home offset X)",
            "$131": "(Home offset Y)",
            "$132": "(Home offset Z)",
        }
        atexit.register(self.disconnect)

    def setup_logging(self, handler=None):
        if handler:
            self._loghandler = handler
        else:
            lh = CallbackLogHandler()
            self._loghandler = lh
        self.logger.addHandler(self._loghandler)
        self._loghandler.callback = self.callback

    def connect(self, path=None, baudrate=115200):
        if path is None or path.strip() == "":
            return
        else:
            self._ifacepath = path
        if self._iface is None:
            self.logger.debug("{}: Setting up interface on {}".format(self.name, self._ifacepath))
            self._iface = Interface("iface_" + self.name, self._ifacepath, baudrate)
            self._iface.start(self._queue)
            print("{}: Setting up interface on {}".format(self.name, self._ifacepath))
        else:
            self.logger.info(
                "{}: Cannot start another interface. There is already an interface {}.".format(self.name, self._iface))
        self._iface_read_do = True
        self.logger.info(f"[MARLIN INIT] Creating _onread thread, _iface_read_do={self._iface_read_do}")
        self._thread_read_iface = threading.Thread(target=self._onread)
        self._thread_read_iface.name = "Marlin interface thread"
        self.logger.info(f"[MARLIN INIT] Starting _onread thread...")
        self._thread_read_iface.start()
        self.logger.info(f"[MARLIN INIT] _onread thread started successfully")
        # Wait for bootup message or timeout
        time.sleep(1)
        # Force bootup initialization if not already done
        if not self.initialized:
            self._on_bootup()

    def disconnect(self):
        if not self.is_connected(): return
        self.logger.info("{}: Disconnecting and stopping all threads...".format(self.name))
        
        # Stop polling first
        self.hash_state_requested = True
        self.gcode_parser_state_requested = True
        self.poll_stop()
        
        # Stop reading thread
        self.logger.debug("{}: Stopping reading thread...".format(self.name))
        self._iface_read_do = False
        
        # Stop the interface (this will close the serial port and interrupt blocking reads)
        try:
            if self._iface:
                self._iface.stop()
        except Exception as e:
            self.logger.warning(f"{self.name}: Error stopping interface: {e}")
        
        # Add dummy message to wake up any blocked queue.get() calls
        try:
            self._queue.put("dummy_msg_for_joining_thread")
        except:
            pass
        
        # Join with timeout to prevent hanging
        if self._thread_read_iface:
            try:
                self._thread_read_iface.join(timeout=2.0)  # 2 second timeout
                if self._thread_read_iface.is_alive():
                    self.logger.warning(f"{self.name}: Reading thread did not stop within timeout")
                else:
                    self.logger.debug("{}: Reading thread successfully joined.".format(self.name))
            except Exception as e:
                self.logger.warning(f"{self.name}: Error joining reading thread: {e}")
        
        # Also need to stop the polling thread with timeout
        if self._thread_polling and self._thread_polling.is_alive():
            try:
                self._thread_polling.join(timeout=1.0)  # 1 second timeout
                if self._thread_polling.is_alive():
                    self.logger.warning(f"{self.name}: Polling thread did not stop within timeout")
            except Exception as e:
                self.logger.warning(f"{self.name}: Error joining polling thread: {e}")
            
        self.logger.info("{}: Disconnect completed.".format(self.name))
        self.connected = False
        self.initialized = False  # Reset initialization flag
        self._iface = None
        self.callback("on_disconnected")

    def set_callback(self, callback):
        self.callback = callback

    def soft_reset(self):
        self._iface_write("M999")
        self.update_preprocessor_position()

    def abort(self):
        if not self.is_connected(): return
        del self._rx_buffer_fill[:]
        del self._rx_buffer_backlog[:]
        self._streaming_enabled = False
        self._wait_empty_buffer = False
        self._streaming_src_end_reached = True
        self._set_streaming_complete(True)
        self._set_job_finished(True)
        self._iface_write("M112")

    def hold(self):
        if not self.is_connected(): return
        self._iface_write("!")

    def resume(self):
        if not self.is_connected(): return
        self._iface_write("~")

    def home(self):
        self.is_homing = True
        self._iface_write("G28")

    def poll_start(self):
        if not self.is_connected(): return
        self._poll_keep_alive = True
        self._last_mode = None
        if self._thread_polling is None:
            self._thread_polling = threading.Thread(target=self._poll_state)
            self._thread_polling.name = "Marlin polling thread"
            self._thread_polling.start()
            self.logger.debug("{}: Polling thread started".format(self.name))
        else:
            self.logger.debug("{}: Polling thread already running...".format(self.name))

    def poll_stop(self):
        if not self.is_connected():
            self._poll_keep_alive = False
            return
        if self._thread_polling is not None:
            self._poll_keep_alive = False
            self.logger.debug("{}: Please wait until polling thread has joined...".format(self.name))
            self._thread_polling.join()
            self.logger.debug("{}: Polling thread has successfully joined...".format(self.name))
        else:
            self.logger.debug("{}: Cannot start a polling thread. Another one is already running.".format(self.name))
        self._thread_polling = None

    def set_feed_override(self, val):
        self.preprocessor.do_feed_override = val

    def request_feed(self, requested_feed):
        self.preprocessor.request_feed = float(requested_feed)

    @property
    def incremental_streaming(self):
        return self._incremental_streaming

    @incremental_streaming.setter
    def incremental_streaming(self, on_off):
        self._incremental_streaming = on_off
        if self._incremental_streaming:
            self._wait_empty_buffer = True
        self.logger.debug("{}: Incremental streaming set to {}".format(self.name, self._incremental_streaming))

    def send_immediately(self, line):
        bytes_in_firmware_buffer = sum(self._rx_buffer_fill)
        if bytes_in_firmware_buffer > 0:
            self.logger.error(
                "Firmware buffer has {:d} unprocessed bytes in it. Will not send {}".format(bytes_in_firmware_buffer,
                                                                                            line))
            return
        if self.current_mode == "Error":
            self.logger.error("Marlin is in ERROR state. Will not send {}.".format(line))
            return
        self.preprocessor.set_line(line)
        self.preprocessor.strip()
        self.preprocessor.tidy()
        self.preprocessor.parse_state()
        self.preprocessor.override_feed()
        self._iface_write(self.preprocessor.line)

    def stream(self, lines):
        # For simple single-line commands, use direct sending to avoid preprocessor issues
        if isinstance(lines, str) and '\n' not in lines.strip():
            simple_commands = ['M17', 'M18', 'M503', 'M110', 'M999', 'G28', 'G90', 'G91', 'G0 ', 'G1 ']
            if any(lines.strip().startswith(cmd) for cmd in simple_commands):
                self.logger.debug(f"Sending simple command directly: {lines}")
                self._iface_write(lines.strip())
                return
        
        # For complex commands or multi-line, use buffering and streaming
        self._load_lines_into_buffer(lines)
        self.job_run()

    def write(self, lines):
        if type(lines) is list:
            lines = "\n".join(lines)
        self._load_lines_into_buffer(lines)

    def job_run(self, line_nr=None):
        if self.buffer_size == 0:
            self.logger.warning("{}: Cannot run job. Nothing in the buffer!".format(self.name))
            return
        if line_nr:
            self.current_line_number = line_nr
        self.travel_dist_current = {}
        self._set_streaming_src_end_reached(False)
        self._set_streaming_complete(False)
        self._streaming_enabled = True
        self._current_line_sent = True
        self._set_job_finished(False)
        self._stream()

    def job_halt(self):
        self._streaming_enabled = False

    def job_new(self):
        del self.buffer[:]
        self.buffer_size = 0
        self._current_line_nr = 0
        self._set_streaming_complete(True)
        self._set_job_finished(True)
        self._set_streaming_src_end_reached(True)
        self._error = False
        # Reset state from Error back to Idle when error is cleared
        if self.current_mode == "Error":
            self.current_mode = "Idle"
        self._current_line = ""
        self._current_line_sent = True
        self.travel_dist_buffer = {}
        self.travel_dist_current = {}

    @property
    def current_line_number(self):
        return self._current_line_nr

    @current_line_number.setter
    def current_line_number(self, linenr):
        if linenr < self.buffer_size:
            self._current_line_nr = linenr

    def request_settings(self):
        self._iface_write("M503")

    def update_preprocessor_position(self):
        self.preprocessor.position_m = list(self.current_position)

    def is_connected(self):
        return self.connected

    def _preprocessor_callback(self, event, *data):
        if event == "on_preprocessor_var_undefined":
            self.logger.critical("HALTED JOB BECAUSE UNDEFINED VAR {}".format(data[0]))
            self._set_streaming_src_end_reached(True)
            self.job_halt()
        else:
            self.callback(event, *data)

    def _stream(self):
        if self._streaming_src_end_reached:
            return
        if not self._streaming_enabled:
            return
        if self.target == "firmware":
            if self._incremental_streaming:
                self._set_next_line()
                if not self._streaming_src_end_reached:
                    self._send_current_line()
                else:
                    self._set_job_finished(True)
            else:
                self._fill_rx_buffer_until_full()
        elif self.target == "simulator":
            buf = []
            while not self._streaming_src_end_reached:
                self._set_next_line(True)
                if self._current_line_nr < self.buffer_size:
                    buf.append(self._current_line)
            self._set_next_line(True)
            buf.append(self._current_line)
            self._set_job_finished(True)
            self.callback("on_simulation_finished", buf)

    def _fill_rx_buffer_until_full(self):
        while True:
            if self._current_line_sent:
                self._set_next_line()
            if self._streaming_src_end_reached == False and self._rx_buf_can_receive_current_line():
                self._send_current_line()
            else:
                break

    def _set_next_line(self, send_comments=False):
        if self._current_line_nr < self.buffer_size:
            line = self.buffer[self._current_line_nr].strip()
            print(f"[MARLIN DEBUG] Setting next line from buffer: '{line}'")
            self.preprocessor.set_line(line)
            self.preprocessor.substitute_vars()
            self.preprocessor.parse_state()
            self.preprocessor.override_feed()
            self.preprocessor.scale_spindle()
            if send_comments:
                self._current_line = self.preprocessor.line + self.preprocessor.comment
            else:
                self._current_line = self.preprocessor.line
            print(f"[MARLIN DEBUG] After preprocessing: '{self._current_line}'")
            self._current_line_sent = False
            self._current_line_nr += 1
            self.preprocessor.done()
        else:
            self._set_streaming_src_end_reached(True)

    def _send_current_line(self):
        self._set_streaming_complete(False)
        line_length = len(self._current_line) + 1
        self._rx_buffer_fill.append(line_length)
        self._rx_buffer_backlog.append(self._current_line)
        self._rx_buffer_backlog_line_number.append(self._current_line_nr)
        print(f"[MARLIN DEBUG] Sending buffer line: '{self._current_line}'")
        self._iface_write(self._current_line)
        self._current_line_sent = True
        
        # Only set to Jog mode for actual movement commands, not status queries
        if not self._is_status_command(self._current_line):
            if self.current_mode != "Jog":
                self.current_mode = "Jog"
                self.callback("on_stateupdate", self.current_mode, self.current_position, self.current_work_position)

    def _rx_buf_can_receive_current_line(self):
        rx_free_bytes = self._rx_buffer_size - sum(self._rx_buffer_fill)
        required_bytes = len(self._current_line) + 1
        return rx_free_bytes >= required_bytes

    def _rx_buffer_fill_pop(self):
        if len(self._rx_buffer_fill) > 0:
            self._rx_buffer_fill.pop(0)
            processed_command = self._rx_buffer_backlog.pop(0)
            ln = self._rx_buffer_backlog_line_number.pop(0) - 1
        if self._streaming_src_end_reached == True and len(self._rx_buffer_fill) == 0:
            self._set_job_finished(True)
            self._set_streaming_complete(True)

    def _iface_write(self, line):
        if self._iface:
            # Add line numbering and checksum for Marlin protocol
            formatted_line = self._format_line_with_checksum(line.strip())
            print(f"[MARLIN DEBUG] Sending: {repr(formatted_line)}")
            self._iface.write(formatted_line)
            # Add configurable delay to prevent buffer overflow and command fragmentation
            import time
            time.sleep(self._command_delay)

    def _format_line_with_checksum(self, line):
        """Format a line with Marlin line number and checksum"""
        # Skip line numbering for emergency/immediate commands and real-time polling
        skip_numbering_commands = ['?', 'M112', '!', '~', '\x18', 'M999', 'M110', 'M114 R']
        
        if any(line.startswith(cmd) for cmd in skip_numbering_commands):
            return line + '\n'
        
        # Format: N<line_number> <command> *<checksum>
        line_with_number = f"N{self._line_number} {line}"
        checksum = self._calculate_checksum(line_with_number)
        formatted = f"{line_with_number}*{checksum}\n"
        
        # Track active numbered commands
        self._active_command_count += 1
        self._line_number += 1
        return formatted

    def _calculate_checksum(self, line):
        """Calculate checksum for Marlin protocol"""
        checksum = 0
        for char in line:
            checksum ^= ord(char)
        return checksum & 0xFF

    def _onread(self):
        self.logger.info(f"[MARLIN THREAD] _onread thread started, _iface_read_do={self._iface_read_do}")
        self.logger.debug(f"[MARLIN THREAD] _onread thread started, _iface_read_do={self._iface_read_do}")
        try:
            while self._iface_read_do:
                line = self._queue.get()
                self.logger.debug(f"[MARLIN QUEUE] Processing line from queue: '{line}'")
                if len(line) > 0:
                    if "echo:busy: processing" in line:
                        self.current_mode = "Jog"
                        self.callback("on_stateupdate", self.current_mode, self.current_position,
                                      self.current_work_position)
                    elif re.search(r'X:(-?[\d.]+) Y:(-?[\d.]+) Z:(-?[\d.]+)', line):
                        print(f"[MARLIN PARSE] Position line regex matched: {line}")
                        self.logger.debug(f"[MARLIN QUEUE] M114 regex matched, calling _update_state_from_m114")
                        self._update_state_from_m114(line)
                    elif line.startswith("echo:"):
                        self._parse_settings(line)
                        self.callback("on_read", line)
                    elif line == "ok":
                        self._handle_ok()
                        self.callback("on_read", line)
                    elif line.startswith("Error:"):
                        self._error = True
                        self.current_mode = "Error"
                        
                        # Use centralized error handlers
                        handled = (
                            MarlinErrorHandler.handle_line_number_error(self, line, self.logger) or
                            MarlinErrorHandler.handle_checksum_error(self, line, self.logger)
                        )
                        
                        self.callback("on_stateupdate", self.current_mode, self.current_position,
                                      self.current_work_position)
                        self.callback("on_read", line)
                        self.callback("on_error", line, "", 0)
                    elif line.startswith("Resend:"):
                        # Use centralized resend handler
                        MarlinErrorHandler.handle_resend_request(self, line, self.logger)
                        self.callback("on_read", line)
                    elif "Unknown command:" in line:
                        # Use centralized command verification
                        is_corrupted, fixed_command = MarlinCommandVerifier.detect_command_corruption(line)
                        if is_corrupted and fixed_command:
                            self.logger.warning(f"COMMAND CORRUPTION DETECTED: {line}")
                            self.logger.info(f"Attempting to fix: {fixed_command}")
                            
                            # Retry if it's a safe command
                            if MarlinCommandVerifier.should_retry_command(self, fixed_command):
                                self.logger.info(f"Auto-retrying fixed command: {fixed_command}")
                                self._iface_write(fixed_command)
                            else:
                                self.logger.warning(f"Command corruption detected but not retrying: {fixed_command}")
                        else:
                            self.logger.warning(f"COMMAND CORRUPTION DETECTED but couldn't fix: {line}")
                        
                        self.callback("on_read", line)
                    elif "Marlin" in line:
                        self.callback("on_read", line)
                        # Initialize Marlin protocol when we detect bootup
                        if not self.initialized:
                            self._on_bootup()
                        self.hash_state_requested = True
                        self.request_settings()
                        self.gcode_parser_state_requested = True
                    else:
                        self.callback("on_read", line)
        except Exception as e:
            self.logger.error(f"Error in _onread thread: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
        finally:
            self.logger.info(f"[MARLIN THREAD] _onread thread is ending")

    def _is_status_command(self, line):
        """Check if a command is just for status/info and doesn't cause movement"""
        status_commands = [
            'M114',  # Get current position
            'M503',  # Get configuration
            'M119',  # Get endstop status  
            'M105',  # Get temperature (if applicable)
            'M115',  # Get firmware info
            '?',     # Grbl status query
        ]
        
        line_upper = line.strip().upper()
        return any(line_upper.startswith(cmd) for cmd in status_commands)

    def _handle_ok(self):
        # Decrement active command counter for numbered commands
        if self._active_command_count > 0:
            self._active_command_count -= 1
            
        if not self.streaming_complete:
            self._rx_buffer_fill_pop()
            if not (self._wait_empty_buffer and len(self._rx_buffer_fill) > 0):
                self._wait_empty_buffer = False
                self._stream()
        else:
            # When streaming is complete and no active commands, allow polling
            if self._active_command_count == 0 and len(self._rx_buffer_fill) == 0:
                self._streaming_enabled = False  # Enable polling when idle

        if self.is_homing:
            self.is_homing = False
            if self.current_mode != "Error":
                self.current_mode = "Idle"
                self.callback("on_idle", "idle")

    def _on_bootup(self):
        self._onboot_init()
        self.initialized = True
        self.connected = True
        self.logger.debug("{}: Marlin has booted!".format(self.name))
        
        # Send M110 to reset line numbering to ensure sync
        self._iface_write("M110 N0")
        self._line_number = 1
        
        self.callback("on_boot")
        self.poll_start()

    def _update_state_from_m114(self, line):
        try:
            self.logger.debug(f"[MARLIN PARSE] Processing M114 line: {line}")
            x_match = re.search(r'X:(-?[\d.]+)', line)
            y_match = re.search(r'Y:(-?[\d.]+)', line)
            z_match = re.search(r'Z:(-?[\d.]+)', line)

            if x_match and y_match and z_match:
                w_pos_x = float(x_match.group(1))
                w_pos_y = float(y_match.group(1))
                w_pos_z = float(z_match.group(1))

                self.current_work_position = (w_pos_x, w_pos_y, w_pos_z)
                self.current_position = self.current_work_position
                print(f"[MARLIN PARSE] Updated position to: {self.current_position}")

                # Handle position change detection
                if self._last_position is None:
                    # First position report after connection - assume standstill
                    self.is_standstill = True
                elif self.current_position != self._last_position:
                    # Position changed - we're moving
                    if self.is_standstill:
                        self.is_standstill = False
                        # Set state to Jog when movement is detected (unless in Error state)
                        if self.current_mode == "Idle":
                            self.current_mode = "Jog"
                        self.callback("on_movement")
                else:
                    # Position unchanged - we've stopped
                    if not self.is_standstill:
                        self.is_standstill = True
                        # Set state back to Idle when movement stops (unless in Error state)
                        if self.current_mode == "Jog":
                            self.current_mode = "Idle"
                            self.callback("on_idle", "idle")
                        self.callback("on_standstill")

                if (self.current_mode != self._last_mode or
                        self.current_position != self._last_position or
                        self.current_work_position != self._last_work_position):
                    self.logger.debug(f"[MARLIN POSITION] Sending on_stateupdate: mode={self.current_mode}, pos={self.current_position}, wpos={self.current_work_position}")
                    print(f"[MARLIN CALLBACK] Sending on_stateupdate: mode={self.current_mode}, pos={self.current_position}, wpos={self.current_work_position}")
                    self.callback("on_stateupdate", self.current_mode, self.current_position,
                                  self.current_work_position)

                self._last_mode = self.current_mode
                self._last_position = self.current_position
                self._last_work_position = self.current_work_position
        except Exception as e:
            self.logger.error(f"Error parsing M114 response: {e} from line: {line}")

    def _parse_settings(self, line):
        try:
            step_match = re.search(r'M92 X(\d+\.\d+) Y(\d+\.\d+) Z(\d+\.\d+) E(\d+\.\d+)', line)
            if step_match:
                self.settings[0] = {"val": step_match.group(1), "cmt": "Steps per unit X"}
                self.settings[1] = {"val": step_match.group(2), "cmt": "Steps per unit Y"}
                self.settings[2] = {"val": step_match.group(3), "cmt": "Steps per unit Z"}
                self.settings[3] = {"val": step_match.group(4), "cmt": "Steps per unit E"}
            feedrate_match = re.search(r'M203 X(\d+\.\d+) Y(\d+\.\d+) Z(\d+\.\d+) E(\d+\.\d+)', line)
            if feedrate_match:
                self.settings[4] = {"val": feedrate_match.group(1), "cmt": "Max feedrate X"}
                self.settings[5] = {"val": feedrate_match.group(2), "cmt": "Max feedrate Y"}
                self.settings[6] = {"val": feedrate_match.group(3), "cmt": "Max feedrate Z"}
                self.settings[7] = {"val": feedrate_match.group(4), "cmt": "Max feedrate E"}
            accel_match = re.search(r'M201 X(\d+) Y(\d+) Z(\d+) E(\d+)', line)
            if accel_match:
                self.settings[8] = {"val": accel_match.group(1), "cmt": "Acceleration X"}
                self.settings[9] = {"val": accel_match.group(2), "cmt": "Acceleration Y"}
                self.settings[10] = {"val": accel_match.group(3), "cmt": "Acceleration Z"}
                self.settings[11] = {"val": accel_match.group(4), "cmt": "Acceleration E"}
            home_offset_match = re.search(r'M206 X([-\d.]+) Y([-\d.]+) Z([-\d.]+)', line)
            if home_offset_match:
                self.settings[130] = {"val": home_offset_match.group(1), "cmt": "Home offset X"}
                self.settings[131] = {"val": home_offset_match.group(2), "cmt": "Home offset Y"}
                self.settings[132] = {"val": home_offset_match.group(3), "cmt": "Home offset Z"}
                x = float(home_offset_match.group(1))
                y = float(home_offset_match.group(2))
                z = float(home_offset_match.group(3))
                self.settings_hash["G54"] = (x, y, z)
                self.callback("on_settings_downloaded", self.settings)
                self.callback("on_hash_stateupdate", self.settings_hash)
        except Exception as e:
            self.logger.error(f"Error parsing settings: {e}")

    def _onboot_init(self):
        del self._rx_buffer_fill[:]
        del self._rx_buffer_backlog[:]
        del self._rx_buffer_backlog_line_number[:]
        self._set_streaming_complete(True)
        self._set_job_finished(True)
        self._set_streaming_src_end_reached(True)
        self._error = False
        # Reset state from Error back to Idle when error is cleared during boot
        if self.current_mode == "Error":
            self.current_mode = "Idle"
        self._current_line = ""
        self._current_line_sent = True
        self._clear_queue()
        self.is_standstill = True  # Assume standstill initially until we detect movement
        # Reset position tracking to avoid false movement detection on first position report
        self._last_position = None
        self._last_work_position = None
        self._line_number = 1  # Reset line numbering on boot
        self._last_resend = None  # Clear any resend tracking
        self._resend_count = 0    # Reset resend counter
        # Enable polling for idle machine - no job running
        self._streaming_enabled = False  # Allow position polling when idle
        self._active_command_count = 0   # Reset command count
        self.preprocessor.reset()

    def _clear_queue(self):
        try:
            junk = self._queue.get_nowait()
            self.logger.debug("Discarding junk %s", junk)
        except:
            pass

    def _poll_state(self):
        while self._poll_keep_alive:
            try:
                # Use centralized polling safety check
                if self._should_poll_position():
                    # Send M114 R for real-time position reporting  
                    self._iface_write("M114 R")
            except:
                traceback.print_exc()
                break
            time.sleep(self.poll_interval)
        self.logger.debug("{}: Polling has been stopped".format(self.name))

    def _should_poll_position(self):
        """Determine if it's safe to send M114 R polling commands"""
        # Allow polling during movement for real-time position updates
        # Only check that we're not overflowing the buffer
        # M114 R is a realtime command that doesn't interfere with movement
        buffer_has_space = sum(self._rx_buffer_fill) < (self._rx_buffer_size - 20)
        return buffer_has_space
    
    def _get_state(self):
        self._iface_write("?")

    def _set_streaming_src_end_reached(self, a):
        self._streaming_src_end_reached = a

    def _set_streaming_complete(self, a):
        self.streaming_complete = a

    def _set_job_finished(self, a):
        if a is True:
            self.callback("on_job_completed")

    def _load_line_into_buffer(self, line):
        print(f"[MARLIN DEBUG] Processing line: '{line}'")
        self.preprocessor.set_line(line)
        split_lines = self.preprocessor.split_lines()
        for l1 in split_lines:
            print(f"[MARLIN DEBUG] Split line: '{l1}'")
            self.preprocessor.set_line(l1)
            self.preprocessor.strip()
            self.preprocessor.tidy()
            self.preprocessor.parse_state()
            self.preprocessor.find_vars()
            fractionized_lines = self.preprocessor.fractionize()
            for l2 in fractionized_lines:
                print(f"[MARLIN DEBUG] Final processed line: '{l2}'")
                self.buffer.append(l2)
                self.buffer_size += 1
            self.preprocessor.done()

    def _load_lines_into_buffer(self, string):
        print(f"[MARLIN DEBUG] Loading into buffer: '{string}'")
        lines = string.split("\n")
        for line in lines:
            self._load_line_into_buffer(line)