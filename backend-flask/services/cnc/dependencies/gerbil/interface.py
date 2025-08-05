import logging
import re
import threading
import time
import traceback

import serial


class Interface:
    def __init__(self, name, port, baudrate=115200):
        self.name = name
        self.port = port
        self.baudrate = baudrate
        self._serial = None
        self._buf = ""
        self.queue = None
        self.logger = logging.getLogger("interface." + self.name)
        self._do_read = False
        self._do_readline = False
        self._thread_read = None

    def start(self, out_queue):
        self.queue = out_queue
        try:
            self._serial = serial.Serial(self.port, self.baudrate, timeout=1)
        except (serial.SerialException, OSError) as e:
            self.logger.error("Could not connect to {}:{} - {}".format(self.port, self.baudrate, e))
            raise e
        self._thread_read = threading.Thread(target=self._run)
        self._thread_read.daemon = True
        self._thread_read.name = "Serial port {}".format(self.port)
        self._do_read = True
        self._thread_read.start()
        self.logger.debug("Serial interface {} connected to port={}, baudrate={}".format(self.name, self.port, self.baudrate))

    def stop(self):
        self._do_read = False
        if self._thread_read:
            if self._thread_read.is_alive():
                self._thread_read.join()
        if self._serial:
            self._serial.close()
            self._serial = None
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
        print(">>>> [INTERFACE] Read thread has started.")
        while self._do_read:
            try:
                if self._serial.isOpen():
                    print(">>>> [INTERFACE] Waiting for data from serial port...")
                    data = self._serial.read_until(bytes("\r\n", "ascii"))
                    if len(data) > 0:
                        print(f">>>> [INTERFACE] RAW DATA RECEIVED: {data}")
                        data_to_process = self._buf + data.decode('ascii')
                        self._buf = ""
                        while True:
                            match = re.search("^([^\r\n]*)\r?\n(.*)", data_to_process, re.S)
                            if not match:
                                self._buf = data_to_process
                                break
                            else:
                                print(f">>>> [INTERFACE] Parsed line and putting into queue: '{match.group(1)}'")
                                self.queue.put(match.group(1))
                                data_to_process = match.group(2)
                                if self.logger.isEnabledFor(9):
                                    self.logger.log(9, "{}:READ: '{}'".format(self.name, match.group(1)))
                    else:
                        print(">>>> [INTERFACE] Serial read timed out (no data).")
                time.sleep(0.04)
            except (serial.SerialException, OSError):
                self.logger.error("Problem during reading the serial port. Retrying every 3 seconds.")
                time.sleep(3)
            except Exception:
                self.logger.error("Unknown problem")
                traceback.print_exc()