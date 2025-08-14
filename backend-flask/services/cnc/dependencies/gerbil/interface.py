import logging
import re
import threading
import time
import traceback

import serial


class Interface:
    def __init__(self, name, port, baudrate=115200):
        self.name = name
        # Extract actual port name from enhanced display name (e.g., "COM10 (STMicroelectronics)" -> "COM10")
        self.port = self._extract_port_name(port)
        self.original_port_display = port  # Keep original for logging
        self.baudrate = baudrate
        self._serial = None
        self._buf = ""
        self.queue = None
        self.logger = logging.getLogger("interface." + self.name)
        self._do_read = False
        self._do_readline = False
        self._thread_read = None

    def _extract_port_name(self, port_display):
        """Extract the actual port name from enhanced display name"""
        # Handle cases like "COM10 (STMicroelectronics)" -> "COM10"
        # Also handle cases like "/dev/ttyUSB0 (Arduino)" -> "/dev/ttyUSB0"
        if '(' in port_display:
            return port_display.split('(')[0].strip()
        return port_display

    def start(self, out_queue):
        self.queue = out_queue
        try:
            self._serial = serial.Serial(self.port, self.baudrate, timeout=1)
        except (serial.SerialException, OSError) as e:
            self.logger.error("Could not connect to {} ({}):{}  - {}".format(self.original_port_display, self.port, self.baudrate, e))
            raise e
        self._thread_read = threading.Thread(target=self._run)
        self._thread_read.daemon = True
        self._thread_read.name = "Serial port {}".format(self.port)
        self._do_read = True
        self._thread_read.start()
        self.logger.debug("Serial interface {} connected to port={} ({}), baudrate={}".format(self.name, self.original_port_display, self.port, self.baudrate))

    def stop(self):
        self.logger.debug("Serial interface {}: Stopping...".format(self.name))
        self._do_read = False
        
        # Close serial port first to interrupt any blocking reads
        if self._serial:
            try:
                self._serial.close()
                self.logger.debug("Serial interface {}: Serial port closed".format(self.name))
            except Exception as e:
                self.logger.warning("Serial interface {}: Error closing serial: {}".format(self.name, e))
            self._serial = None
        
        # Join the read thread with timeout
        if self._thread_read:
            if self._thread_read.is_alive():
                try:
                    self._thread_read.join(timeout=2.0)  # 2 second timeout
                    if self._thread_read.is_alive():
                        self.logger.warning("Serial interface {}: Read thread did not stop within timeout - forcing shutdown".format(self.name))
                        # Force thread to exit by setting daemon and letting it be garbage collected
                        self._thread_read.daemon = True
                    else:
                        self.logger.debug("Serial interface {}: Read thread stopped successfully".format(self.name))
                except Exception as e:
                    self.logger.warning("Serial interface {}: Error joining read thread: {}".format(self.name, e))
        
        self.logger.debug("Serial interface {} closed.".format(self.name))

    def write(self, data):
        if not self._serial:
            return 0
        try:
            data_binary = data.encode()
            num_written = self._serial.write(data_binary)
            if self.logger.isEnabledFor(9):
                prettified = data.rstrip('\r\n')
                self.logger.log(9, "{}:WRITE: '{}'".format(self.name, prettified))
            return num_written
        except (serial.SerialTimeoutException, serial.SerialException) as e:
            self.logger.debug(str(e))
            return 0

    def _run(self):
        while self._do_read:
            try:
                if self._serial and self._serial.isOpen():
                    # Use read() with timeout instead of read_until() to prevent blocking
                    data = self._serial.read(1024)  # Read up to 1024 bytes
                    if len(data) > 0:
                        try:
                            data_to_process = self._buf + data.decode('ascii', errors='ignore')
                            self._buf = ""
                            while True:
                                match = re.search("^([^\r\n]*)\r?\n(.*)", data_to_process, re.S)
                                if not match:
                                    self._buf = data_to_process
                                    break
                                else:
                                    line = match.group(1)
                                    if line:  # Only process non-empty lines
                                        self.queue.put(line)
                                        if self.logger.isEnabledFor(9):
                                            self.logger.log(9, "{}:READ: '{}'".format(self.name, line))
                                    data_to_process = match.group(2)
                        except UnicodeDecodeError:
                            # Skip corrupted data silently  
                            self._buf = ""
                    else:
                        # No data available, check if we should continue
                        if not self._do_read:
                            break
                else:
                    # Serial port is closed, break the loop
                    break
                time.sleep(0.01)  # Small delay to prevent CPU spinning
            except (serial.SerialException, OSError) as e:
                if not self._do_read:
                    # Expected exception when stopping
                    break
                self.logger.error("Problem during reading the serial port. Retrying every 3 seconds.")
                # Check _do_read during retry wait to allow immediate shutdown
                for _ in range(30):  # 30 * 0.1s = 3 seconds total
                    if not self._do_read:
                        return  # Exit immediately if shutdown requested
                    time.sleep(0.1)
            except Exception:
                if not self._do_read:
                    # Expected exception when stopping
                    break
                self.logger.error("Unknown problem")
                traceback.print_exc()