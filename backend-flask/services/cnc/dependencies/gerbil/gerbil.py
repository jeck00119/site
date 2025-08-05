"""
Gerbil - Copyright (c) 2015 Michael Franzl

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import atexit
import logging
import re
import threading
import time
import traceback
from queue import Queue

from .callbackloghandler import CallbackLogHandler
from .gcode_machine import GcodeMachine
from .interface import Interface


class Gerbil:
    def __init__(self, callback, name="mygrbl"):
        self.name = name
        self.cmode = None
        self.cmpos = (0, 0, 0)
        self.cwpos = (0, 0, 0)
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
        self.poll_interval = 0.2
        self.settings = {
            130: {"val": "1000", "cmt": "width"},
            131: {"val": "1000", "cmt": "height"}
        }
        self.settings_hash = {
            "G54": (-600, -300, 0),
            "G55": (-400, -300, 0),
            "G56": (-200, -300, 0),
            "G57": (-600, -600, 0),
            "G58": (-400, -600, 0),
            "G59": (-200, -600, 0),
            "G28": (0, 0, 0),
            "G30": (0, 0, 0),
            "G92": (0, 0, 0),
            "TLO": 0,
            "PRB": (0, 0, 0),
        }
        self.gcode_parser_state_requested = False
        self.hash_state_requested = False
        self.logger = logging.getLogger("gerbil")
        self.logger.setLevel(5)
        self.logger.propagate = False
        self.target = "firmware"
        self.connected = False
        self.preprocessor = GcodeMachine()
        self.preprocessor.callback = self._preprocessor_callback
        self.travel_dist_buffer = {}
        self.travel_dist_current = {}
        self.is_standstill = False
        self._ifacepath = None
        self._last_setting_number = 132
        self._last_cmode = None
        self._last_cmpos = (0, 0, 0)
        self._last_cwpos = (0, 0, 0)
        self._standstill_watchdog_increment = 0
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
        self._streaming_enabled = True
        self._error = False
        self._incremental_streaming = False
        self._hash_state_sent = False
        self.buffer = []
        self.buffer_size = 0
        self._current_line_nr = 0
        self.buffer_stash = []
        self.buffer_size_stash = 0
        self._current_line_nr_stash = 0
        self._poll_keep_alive = False
        self._iface_read_do = False
        self._thread_polling = None
        self._thread_read_iface = None
        self._iface = None
        self._queue = Queue()
        self._loghandler = None
        self._counter = 0
        self.callback = callback
        atexit.register(self.disconnect)
        self.callback("on_settings_downloaded", self.settings)
        self.callback("on_hash_stateupdate", self.settings_hash)
        self.preprocessor.cs_offsets = self.settings_hash
        self.callback("on_gcode_parser_stateupdate", self.gps)

    def change_gui(self):
        self.callback("on_settings_downloaded", self.settings)
        self.callback("on_hash_stateupdate", self.settings_hash)
        self.preprocessor.cs_offsets = self.settings_hash
        self.callback("on_gcode_parser_stateupdate", self.gps)

    def get_status(self):
        if not self.is_connected():
            return False
        else:
            return True

    def setup_logging(self, handler=None):
        if handler:
            self._loghandler = handler
        else:
            lh = CallbackLogHandler()
            self._loghandler = lh
        self.logger.addHandler(self._loghandler)
        self._loghandler.callback = self.callback

    def cnect(self, path=None, baudrate=115200):
        if path is None or path.strip() == "":
            return
        else:
            self._ifacepath = path
        if self._iface is None:
            self.logger.debug("{}: Setting up interface on {}".format(self.name, self._ifacepath))
            self._iface = Interface("iface_" + self.name, self._ifacepath, baudrate)
            self._iface.start(self._queue)
        else:
            self.logger.info("{}: Cannot start another interface. There is already an interface {}.".format(self.name, self._iface))
        self._iface_read_do = True
        self._thread_read_iface = threading.Thread(target=self._onread)
        self._thread_read_iface.name = "Gerbil interface thread"
        self._thread_read_iface.start()
        self.soft_reset()

    def disconnect(self):
        if not self.is_connected(): return
        self.hash_state_requested = True
        self.gcode_parser_state_requested = True
        self._iface.stop()
        self.logger.debug("{}: Please wait until reading thread has joined...".format(self.name))
        self._iface_read_do = False
        self._queue.put("dummy_msg_for_joining_thread")
        self._thread_read_iface.join()
        self.logger.debug("{}: Reading thread successfully joined.".format(self.name))
        self.poll_stop()
        self.connected = False
        self._iface = None
        self.callback("on_disconnected")

    def set_callback(self, callback):
        self.callback = callback

    def soft_reset(self):
        self._iface.write("\x18")
        self.update_preprocessor_position()

    def abort(self):
        if not self.is_connected(): return
        self.soft_reset()

    def hold(self):
        if not self.is_connected(): return
        self._iface_write("!")

    def resume(self):
        if not self.is_connected(): return
        self._iface_write("~")

    def killalarm(self):
        self._iface_write("$X\n")

    def homing(self):
        self._iface_write("$H\n")

    def poll_start(self):
        if not self.is_connected(): return
        self._poll_keep_alive = True
        self._last_cmode = None
        if self._thread_polling is None:
            self._thread_polling = threading.Thread(target=self._poll_state)
            self._thread_polling.name = "Gerbil pooling thread"
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
            self.logger.debug("{}: Polling thread has successfully  joined...".format(self.name))
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
            self.logger.error("Firmware buffer has {:d} unprocessed bytes in it. Will not send {}".format(bytes_in_firmware_buffer, line))
            return
        if self.cmode == "Alarm":
            self.logger.error("Grbl is in ALARM state. Will not send {}.".format(line))
            return
        if self.cmode == "Hold":
            self.logger.error("Grbl is in HOLD state. Will not send {}.".format(line))
            return
        if "$#" in line:
            self.hash_state_requested = True
            return
        self.preprocessor.set_line(line)
        self.preprocessor.strip()
        self.preprocessor.tidy()
        self.preprocessor.parse_state()
        self.preprocessor.override_feed()
        self._iface_write(self.preprocessor.line + "\n")

    def stream(self, lines):
        self._load_lines_into_buffer(lines)
        self.job_run()

    def write(self, lines):
        if type(lines) is list:
            lines = "\n".join(lines)
        self._load_lines_into_buffer(lines)

    def load_file(self, filename):
        if not self.job_finished:
            self.logger.warning("{}: Job must be finished before you can load a file".format(self.name))
            return
        self.job_new()
        with open(filename) as f:
            self._load_lines_into_buffer(f.read())

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
        self.callback("on_line_number_change", 0)
        self.callback("on_bufsize_change", 0)
        self._set_streaming_complete(True)
        self.job_finished = True
        self._set_streaming_src_end_reached(True)
        self._error = False
        self._current_line = ""
        self._current_line_sent = True
        self.travel_dist_buffer = {}
        self.travel_dist_current = {}
        self.callback("on_vars_change", self.preprocessor.vars)

    @property
    def current_line_number(self):
        return self._current_line_nr

    @current_line_number.setter
    def current_line_number(self, linenr):
        if linenr < self.buffer_size:
            self._current_line_nr = linenr
            self.callback("on_line_number_change", self._current_line_nr)

    def request_settings(self):
        self._iface_write("$$\n")

    def do_buffer_stash(self):
        self.buffer_stash = list(self.buffer)
        self.buffer_size_stash = self.buffer_size
        self._current_line_nr_stash = self._current_line_nr
        self.job_new()

    def do_buffer_unstash(self):
        self.buffer = list(self.buffer_stash)
        self.buffer_size = self.buffer_size_stash
        self.current_line_number = self._current_line_nr_stash
        self.callback("on_bufsize_change", self.buffer_size)

    def update_preprocessor_position(self):
        self.preprocessor.position_m = list(self.cmpos)

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
        progress_percent = int(100 * self._current_line_nr / self.buffer_size)
        self.callback("on_progress_percent", progress_percent)
        if self._current_line_nr < self.buffer_size:
            line = self.buffer[self._current_line_nr].strip()
            self.preprocessor.set_line(line)
            self.preprocessor.substitute_vars()
            self.preprocessor.parse_state()
            self.preprocessor.override_feed()
            self.preprocessor.scale_spindle()
            if send_comments:
                self._current_line = self.preprocessor.line + self.preprocessor.comment
            else:
                self._current_line = self.preprocessor.line
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
        self._iface_write(self._current_line + "\n")
        self._current_line_sent = True
        self.callback("on_line_sent", self._current_line_nr, self._current_line)

    def _rx_buf_can_receive_current_line(self):
        rx_free_bytes = self._rx_buffer_size - sum(self._rx_buffer_fill)
        required_bytes = len(self._current_line) + 1
        return rx_free_bytes >= required_bytes

    def _rx_buffer_fill_pop(self):
        if len(self._rx_buffer_fill) > 0:
            self._rx_buffer_fill.pop(0)
            processed_command = self._rx_buffer_backlog.pop(0)
            ln = self._rx_buffer_backlog_line_number.pop(0) - 1
            self.callback("on_processed_command", ln, processed_command)
        if self._streaming_src_end_reached == True and len(self._rx_buffer_fill) == 0:
            self._set_job_finished(True)
            self._set_streaming_complete(True)

    def _iface_write(self, line):
        self.callback("on_write", line)
        if self._iface:
            num_written = self._iface.write(line)

    def _onread(self):
        while self._iface_read_do:
            line = self._queue.get()
            if len(line) > 0:
                if line[0] == "<":
                    self._update_state(line)
                elif "MSG" in line:
                    self.callback("on_read", line)
                elif line == "ok":
                    self._handle_ok()
                elif re.match("^\[G[0123] .*", line):
                    self._update_gcode_parser_state(line)
                    self.callback("on_read", line)
                elif re.match("^\[...:.*", line):
                    self._update_hash_state(line)
                    self.callback("on_read", line)
                    if "PRB" in line:
                        if self.hash_state_requested:
                            self._hash_state_sent = False
                            self.hash_state_requested = False
                            self.callback("on_hash_stateupdate", self.settings_hash)
                            self.preprocessor.cs_offsets = self.settings_hash
                        else:
                            self.callback("on_probe", self.settings_hash["PRB"])
                elif "ALARM" in line:
                    self.cmode = "Alarm"
                    self.callback("on_stateupdate", self.cmode, self.cmpos, self.cwpos)
                    self.callback("on_read", line)
                    self.callback("on_alarm", line)
                elif "error" in line:
                    self._error = True
                    if len(self._rx_buffer_backlog) > 0:
                        problem_command = self._rx_buffer_backlog[0]
                        problem_line = self._rx_buffer_backlog_line_number[0]
                    else:
                        problem_command = "unknown"
                        problem_line = -1
                    self.callback("on_error", line, problem_command, problem_line)
                    self._set_streaming_complete(True)
                    self._set_streaming_src_end_reached(True)
                elif "Grbl " in line:
                    self.callback("on_read", line)
                    self._on_bootup()
                    self.hash_state_requested = True
                    self.request_settings()
                    self.gcode_parser_state_requested = True
                else:
                    m = re.match("\$(.*)=(.*)", line)
                    if m:
                        key = int(m.group(1))
                        val = m.group(2)
                        self.settings[key] = {
                            "val": val,
                            "cmt": 'comment'
                        }
                        self.callback("on_read", line)
                        if key == self._last_setting_number:
                            self.callback("on_settings_downloaded", self.settings)
                    else:
                        self.callback("on_read", line)

    def _handle_ok(self):
        if not self.streaming_complete:
            self._rx_buffer_fill_pop()
            if not (self._wait_empty_buffer and len(self._rx_buffer_fill) > 0):
                self._wait_empty_buffer = False
                self._stream()
        self._rx_buffer_fill_percent = int(100 - 100 * (self._rx_buffer_size - sum(self._rx_buffer_fill)) / self._rx_buffer_size)
        self.callback("on_rx_buffer_percent", self._rx_buffer_fill_percent)

    def _on_bootup(self):
        self._onboot_init()
        self.connected = True
        self.logger.debug("{}: Grbl has booted!".format(self.name))
        self.callback("on_boot")
        self.poll_start()

    def _update_hash_state(self, line):
        line = line.replace("]", "").replace("[", "")
        parts = line.split(":")
        key = parts[0]
        if key == "HLP":
            print(line)
        else:
            tpl_str = parts[1].split(",")
            tpl = []
            for x in tpl_str:
                try:
                    t = float(x)
                except ValueError:
                    t = 0.0
                tpl.append(t)
            self.settings_hash[key] = tuple(tpl)

    def _update_gcode_parser_state(self, line):
        m = re.match("\[G(\d) G(\d\d) G(\d\d) G(\d\d) G(\d\d) G(\d\d) M(\d) M(\d) M(\d) T(\d) F([\d.-]*?) S([\d.-]*?)\]", line)
        if m:
            self.gps[0] = m.group(1)
            self.gps[1] = m.group(2)
            self.gps[2] = m.group(3)
            self.gps[3] = m.group(4)
            self.gps[4] = m.group(5)
            self.gps[5] = m.group(6)
            self.gps[6] = m.group(7)
            self.gps[7] = m.group(8)
            self.gps[8] = m.group(9)
            self.gps[9] = m.group(10)
            self.gps[10] = m.group(11)
            self.gps[11] = m.group(12)
            self.callback("on_gcode_parser_stateupdate", self.gps)
            self.update_preprocessor_position()
        else:
            self.logger.error("{}: Could not parse gcode parser report: '{}'".format(self.name, line))

    def _update_state(self, line):
        if "FS" not in line:
            if "WCO" in line or "Ov" in line:
                res = [i for i in range(len(line)) if line.startswith("|", i)]
                line = line[:res[1]] + "|FS:0,0" + line[res[1]:]
            else:
                line = line[:-1] + "|FS:0,0>"
        try:
            m = re.match(
                "<([0-9A-z:]*)[|,]MPos:(-?\d+\.\d{3}),(-?\d+\.\d{3}),(-?\d+\.\d{3})[|,](?:Bf:-?\d+,-?\d+[|,])?FS:-?\d+,-?\d+[|,]?(?:Pn:[XYZPDHRS]+[|,]?)?(?:WCO:(-?\d+\.\d{3}),(-?\d+\.\d{3}),(-?\d+\.\d{3})[|,]?)?(?:Ov:(-?\d+),(-?\d+),(-?\d+)[|,]?)?(?:A:[SCFM]+)?>",
                line)
            state = m.group(1)
            m_pos_x = m.group(2)
            m_pos_y = m.group(3)
            m_pos_z = m.group(4)
            w_pos_x = m.group(5)
            w_pos_y = m.group(6)
            w_pos_z = m.group(7)
            self.cmode = state
            self.cmpos = (float(m_pos_x), float(m_pos_y), float(m_pos_z))
            if w_pos_x is not None:
                self.cwpos = (float(w_pos_x), float(w_pos_y), float(w_pos_z))
        except AttributeError:
            pass
        if (self.cmode != self._last_cmode or
                self.cmpos != self._last_cmpos or
                self.cwpos != self._last_cwpos):
            self.callback("on_stateupdate", self.cmode, self.cmpos, self.cwpos)
            if self.streaming_complete == True and self.cmode == "Idle":
                self.update_preprocessor_position()
                self.gcode_parser_state_requested = True
        if self.cmpos != self._last_cmpos:
            if self.is_standstill:
                self._standstill_watchdog_increment = 0
                self.is_standstill = False
                self.callback("on_movement")
        else:
            self._standstill_watchdog_increment += 1
        if self.is_standstill is False and self._standstill_watchdog_increment > 10:
            self.is_standstill = True
            self.callback("on_standstill")
        self._last_cmode = self.cmode
        self._last_cmpos = self.cmpos
        self._last_cwpos = self.cwpos
        if 'Idle' in line:
            self.callback("on_idle", 'idle')
            return
        if 'Alarm' in line:
            self.callback("on_idle", 'alarm')
            return
        if 'Jog' in line:
            self.callback("on_idle", 'jog')
            return

    def _load_line_into_buffer(self, line):
        self.preprocessor.set_line(line)
        split_lines = self.preprocessor.split_lines()
        for l1 in split_lines:
            self.preprocessor.set_line(l1)
            self.preprocessor.strip()
            self.preprocessor.tidy()
            self.preprocessor.parse_state()
            self.preprocessor.find_vars()
            fractionized_lines = self.preprocessor.fractionize()
            for l2 in fractionized_lines:
                self.buffer.append(l2)
                self.buffer_size += 1
            self.preprocessor.done()

    def _load_lines_into_buffer(self, string):
        lines = string.split("\n")
        for line in lines:
            self._load_line_into_buffer(line)
        self.callback("on_bufsize_change", self.buffer_size)
        self.callback("on_vars_change", self.preprocessor.vars)

    def is_connected(self):
        if not self.connected:
            pass
        return self.connected

    def _onboot_init(self):
        del self._rx_buffer_fill[:]
        del self._rx_buffer_backlog[:]
        del self._rx_buffer_backlog_line_number[:]
        self._set_streaming_complete(True)
        self._set_job_finished(True)
        self._set_streaming_src_end_reached(True)
        self._error = False
        self._current_line = ""
        self._current_line_sent = True
        self._clear_queue()
        self.is_standstill = False
        self.preprocessor.reset()
        self.callback("on_progress_percent", 0)
        self.callback("on_rx_buffer_percent", 0)

    def _clear_queue(self):
        try:
            junk = self._queue.get_nowait()
            self.logger.debug("Discarding junk %s", junk)
        except:
            pass

    def _poll_state(self):
        while self._poll_keep_alive:
            try:
                self._counter += 1
                if self.hash_state_requested:
                    self.get_hash_state()
                    self.hash_state_requested = False
                elif self.gcode_parser_state_requested:
                    self.get_gcode_parser_state()
                    self.gcode_parser_state_requested = False
                else:
                    self._get_state()
            except:
                traceback.print_exc()
                break
            time.sleep(self.poll_interval)
        self.logger.debug("{}: Polling has been stopped".format(self.name))

    def is_poll_alive(self):
        return self._poll_keep_alive

    def _get_state(self):
        self._iface.write("?")

    def get_gcode_parser_state(self):
        self._iface_write("$G\n")

    def get_hash_state(self):
        if self.cmode == "Hold":
            self.hash_state_requested = False
            self.logger.info("{}: $# command not supported in Hold mode.".format(self.name))
            return
        if not self._hash_state_sent:
            self._iface_write("$#\n")
            self._hash_state_sent = True

    def _set_streaming_src_end_reached(self, a):
        self._streaming_src_end_reached = a

    def _set_streaming_complete(self, a):
        self.streaming_complete = a

    def _set_job_finished(self, a):
        self.job_finished = a
        if a == True:
            self.callback("on_job_completed")