import html  # Import the html module for escaping
import serial
import serial.tools.list_ports
import sys
import time

from PyQt5.QtCore import QTimer, QEvent, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QComboBox, QPushButton, QTextEdit, QLabel, QLineEdit, QGridLayout,
                             QGroupBox, QStatusBar, QMessageBox, QSpinBox, QCheckBox)


class CNCController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_connection = None
        self.command_history = []
        self.history_position = -1
        # Make QTimer available within the class instance
        self.QTimer = QTimer
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('CNC Controller')
        self.setGeometry(100, 100, 650, 500)

        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Connection section ---
        conn_layout = QHBoxLayout()
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_combo = QComboBox()
        port_layout.addWidget(self.port_combo, 1)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_ports)
        port_layout.addWidget(self.refresh_button)

        baud_layout = QHBoxLayout()
        baud_layout.addWidget(QLabel("Baud:"))
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "115200", "250000"])
        self.baud_combo.setCurrentText("115200")
        baud_layout.addWidget(self.baud_combo, 1)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        self.connect_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

        conn_left = QVBoxLayout()
        conn_left.addLayout(port_layout)
        conn_left.addLayout(baud_layout)

        conn_right = QVBoxLayout()
        # --- Changed ABORT button to HALT ---
        self.halt_button = QPushButton("HALT Movement") # Renamed button
        self.halt_button.setMinimumHeight(50)
        self.halt_button.setFont(QFont("Arial", 12, QFont.Bold))
        # Changed color slightly to differentiate from emergency stop
        self.halt_button.setStyleSheet("background-color: #FFA500; color: white; font-weight: bold;")
        # Connect HALT button to the new halt_movement function
        self.halt_button.clicked.connect(self.halt_movement)
        conn_right.addWidget(self.connect_button)
        conn_right.addWidget(self.halt_button) # Add halt_button instead of abort_button

        conn_layout.addLayout(conn_left, 2)
        conn_layout.addLayout(conn_right, 1)

        # --- Movement controls ---
        move_group = QGroupBox("Movement Controls")
        # Use a single layout for the group box content
        move_group_layout = QVBoxLayout() # Changed to QVBoxLayout for better structure

        # Settings layout within the group box
        settings_layout = QGridLayout()
        settings_layout.addWidget(QLabel("Feedrate:"), 0, 0)
        self.feedrate_input = QSpinBox()
        self.feedrate_input.setRange(10, 5000)
        self.feedrate_input.setValue(500)
        settings_layout.addWidget(self.feedrate_input, 0, 1)

        settings_layout.addWidget(QLabel("Step:"), 0, 2)
        self.step_input = QSpinBox()
        self.step_input.setRange(1, 100)
        self.step_input.setValue(5)
        settings_layout.addWidget(self.step_input, 0, 3)

        self.enable_motors_checkbox = QCheckBox("Enable Motors (M17) on Move")
        self.enable_motors_checkbox.setChecked(True)
        # Span the checkbox across fewer columns if needed, or add stretch
        settings_layout.addWidget(self.enable_motors_checkbox, 1, 0, 1, 4)
        move_group_layout.addLayout(settings_layout) # Add settings to group layout


        # Axis buttons layout within the group box
        axis_layout = QGridLayout()
        btn_style = "font-size: 14px; font-weight: bold; background-color: #3498db; color: white; min-width: 40px; min-height: 40px;"

        # X Axis
        self.btn_x_up = QPushButton("▲")
        self.btn_x_up.setStyleSheet(btn_style)
        self.btn_x_up.clicked.connect(lambda: self.move_axis("X", 1))
        x_label = QLabel("X")
        x_label.setAlignment(Qt.AlignCenter)
        x_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_x_down = QPushButton("▼")
        self.btn_x_down.setStyleSheet(btn_style)
        self.btn_x_down.clicked.connect(lambda: self.move_axis("X", -1))
        axis_layout.addWidget(self.btn_x_up, 0, 0)
        axis_layout.addWidget(x_label, 1, 0)
        axis_layout.addWidget(self.btn_x_down, 2, 0)

        # Y Axis
        self.btn_y_up = QPushButton("▲")
        self.btn_y_up.setStyleSheet(btn_style)
        self.btn_y_up.clicked.connect(lambda: self.move_axis("Y", 1))
        y_label = QLabel("Y")
        y_label.setAlignment(Qt.AlignCenter)
        y_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_y_down = QPushButton("▼")
        self.btn_y_down.setStyleSheet(btn_style)
        self.btn_y_down.clicked.connect(lambda: self.move_axis("Y", -1))
        axis_layout.addWidget(self.btn_y_up, 0, 1)
        axis_layout.addWidget(y_label, 1, 1)
        axis_layout.addWidget(self.btn_y_down, 2, 1)

        # Z Axis
        self.btn_z_up = QPushButton("▲")
        self.btn_z_up.setStyleSheet(btn_style)
        self.btn_z_up.clicked.connect(lambda: self.move_axis("Z", 1))
        z_label = QLabel("Z")
        z_label.setAlignment(Qt.AlignCenter)
        z_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_z_down = QPushButton("▼")
        self.btn_z_down.setStyleSheet(btn_style)
        self.btn_z_down.clicked.connect(lambda: self.move_axis("Z", -1))
        axis_layout.addWidget(self.btn_z_up, 0, 2)
        axis_layout.addWidget(z_label, 1, 2)
        axis_layout.addWidget(self.btn_z_down, 2, 2)

        move_group_layout.addLayout(axis_layout) # Add axis buttons to group layout
        move_group.setLayout(move_group_layout) # Set the group box's layout

        # --- Common commands ---
        # Put common commands inside their own GroupBox for better organization
        common_commands_group = QGroupBox("Common Commands")
        cmd_layout = QHBoxLayout() # Layout for the buttons inside the group
        cmd_style = "padding: 5px;" # Slightly more padding

        commands = [
            ("Home All", "G28"),
            ("Home X", "G28 X"),
            ("Home Y", "G28 Y"),
            ("Home Z", "G28 Z"),
            ("Get Pos", "M114")
            # Consider adding ("Unlock", "$X") if using Grbl
            # Consider adding ("Resume", "~") if needed often
        ]

        for label, cmd in commands:
            btn = QPushButton(label)
            btn.setStyleSheet(cmd_style)
            # Use lambda with default argument to capture correct command
            btn.clicked.connect(lambda checked, c=cmd: self.send_and_wait(c))
            cmd_layout.addWidget(btn)
        common_commands_group.setLayout(cmd_layout) # Set layout for the group

        # --- Terminal ---
        terminal_group = QGroupBox("Terminal") # Put terminal in a groupbox
        terminal_layout = QVBoxLayout() # Layout for terminal group

        terminal_header = QHBoxLayout()
        # terminal_header.addWidget(QLabel("Terminal:")) # Label might be redundant with GroupBox title
        terminal_header.addStretch() # Push clear button to the right
        self.clear_terminal_button = QPushButton("Clear")
        self.clear_terminal_button.clicked.connect(self.clear_terminal)
        terminal_header.addWidget(self.clear_terminal_button)
        terminal_layout.addLayout(terminal_header)

        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, Monospace;") # Dark theme
        self.terminal_output.setMinimumHeight(150)
        terminal_layout.addWidget(self.terminal_output)

        # Command input
        cmd_input_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter G-code command (e.g., G0 X10, M114, ~ to resume)...")
        self.command_input.returnPressed.connect(self.send_command)
        # Install event filter for history navigation
        self.command_input.installEventFilter(self)
        cmd_input_layout.addWidget(self.command_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_command)
        self.send_button.setStyleSheet("background-color: #008CBA; color: white;")
        cmd_input_layout.addWidget(self.send_button)

        terminal_layout.addLayout(cmd_input_layout)
        terminal_group.setLayout(terminal_layout) # Set layout for terminal group

        # Add all sections to main layout
        main_layout.addLayout(conn_layout)
        main_layout.addWidget(move_group)
        main_layout.addWidget(common_commands_group) # Add common commands group
        main_layout.addWidget(terminal_group, 1) # Add terminal group, give it stretch factor

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Disconnected")

        # Read timer for serial data
        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_serial_data)

        # Initial setup
        self.refresh_ports()
        self.enable_ui_elements(False) # Disable controls initially

    def move_axis(self, axis, direction):
        """Sends commands to move a specific axis."""
        if not self.serial_connection or not self.serial_connection.is_open:
            self.append_to_terminal("Cannot move: Not connected.", False)
            return

        try:
            # Disable buttons during movement to prevent spamming
            # self.disable_axis_buttons() # Maybe not disable for jogging? Allows quick stops.

            # Get parameters from UI
            step = self.step_input.value()
            feedrate = self.feedrate_input.value()
            distance = step * direction

            # Enable motors if the checkbox is checked (only if needed)
            # This assumes the controller might disable motors automatically
            # or they were disabled by M18 previously.
            if self.enable_motors_checkbox.isChecked():
                self.send_and_wait("M17") # Enable motors
                # A small delay might be needed ONLY if M17 takes time, otherwise remove.
                # time.sleep(0.05)

            # Send movement commands
            self.send_and_wait("G91") # Set to relative positioning for jogging
            self.send_and_wait(f"G1 {axis}{distance} F{feedrate}") # Send move command
            self.send_and_wait("G90") # Set back to absolute positioning (good practice)

            # Request position update after move (optional, can clutter terminal)
            # self.send_and_wait("M114")

            # Re-enable buttons if they were disabled
            # self.QTimer.singleShot(100, self.enable_axis_buttons) # Quick re-enable if disabled

        except Exception as e:
            self.append_to_terminal(f"ERROR during move: {str(e)}", False)
            # Ensure buttons are re-enabled if an error occurs and they were disabled
            # self.enable_axis_buttons()

    def send_and_wait(self, command):
        """Sends a command and logs it to the terminal."""
        if not self.serial_connection or not self.serial_connection.is_open:
            self.append_to_terminal("Cannot send: Not connected.", False)
            return

        try:
            self.append_to_terminal(command, True) # Log command being sent
            command_bytes = (command + '\r\n').encode('utf-8') # Add newline and encode
            self.serial_connection.write(command_bytes)
            self.serial_connection.flush() # Ensure data is sent
            # Reduce delay further or remove if controller handles commands quickly
            time.sleep(0.02)
        except serial.SerialTimeoutException as e: # Catch specific timeout error
             self.append_to_terminal(f"ERROR sending command '{command}': Write Timeout. Controller may be busy or unresponsive.", False)
             self.status_bar.showMessage("Write Timeout: Controller busy/unresponsive?")
        except Exception as e:
            self.append_to_terminal(f"ERROR sending command '{command}': {str(e)}", False)

    def disable_axis_buttons(self):
        """Disables all axis movement buttons."""
        for btn in [self.btn_x_up, self.btn_x_down, self.btn_y_up,
                    self.btn_y_down, self.btn_z_up, self.btn_z_down]:
            btn.setEnabled(False)

    def enable_axis_buttons(self):
        """Enables axis movement buttons if connected."""
        is_connected = self.serial_connection and self.serial_connection.is_open
        for btn in [self.btn_x_up, self.btn_x_down, self.btn_y_up,
                    self.btn_y_down, self.btn_z_up, self.btn_z_down]:
            btn.setEnabled(is_connected)

    # --- Renamed emergency_stop to halt_movement ---
    def halt_movement(self):
        """
        Sends a Feed Hold command (!) to pause motion without locking the controller.
        """
        # Check if the serial connection is valid and open
        if not self.serial_connection or not self.serial_connection.is_open:
            self.status_bar.showMessage("Cannot HALT: No Serial Connection")
            self.append_to_terminal("Cannot HALT: No Serial Connection", False)
            return

        try:
            # --- Send Feed Hold ---
            self.append_to_terminal("--- HALTING MOVEMENT ---", True)
            print("HALT MOVEMENT ACTIVATED")

            # Send the standard Feed Hold character (!)
            # Most Grbl-based controllers and some Marlin versions respond to this.
            feed_hold_char = b'!'
            self.serial_connection.write(feed_hold_char)
            self.append_to_terminal("SENT: ! (Feed Hold)", True)

            # Update status bar - motion should pause.
            # User can send '~' (Resume) or new G-code commands.
            self.status_bar.showMessage("Movement Halted (Feed Hold). Send ~ to resume.")
            self.append_to_terminal("Movement should pause. Send ~ to resume or new commands.", False)

            # --- IMPORTANT ---
            # DO NOT disable motors (M18) unless you specifically want that behaviour.
            # DO NOT disable UI buttons, allow user to send Resume or other commands.
            # DO NOT send M112 or other commands that lock the controller.

        except serial.SerialTimeoutException as e:
             # Handle potential timeout even during the halt command
             error_msg = f"TIMEOUT sending Feed Hold (!): {str(e)}. Controller unresponsive?"
             print(error_msg)
             self.append_to_terminal(error_msg, False)
             self.status_bar.showMessage("Halt Timeout: Controller unresponsive?")
        except Exception as e:
            error_msg = f"ERROR sending Feed Hold (!): {str(e)}"
            print(error_msg)
            self.append_to_terminal(error_msg, False)
            self.status_bar.showMessage(f"Halt Error: {str(e)}")

    # --- End of halt_movement Function ---

    # --- Optional: Add a function for Resume ---
    def resume_movement(self):
        """Sends a Resume command (~)"""
        if not self.serial_connection or not self.serial_connection.is_open:
            self.append_to_terminal("Cannot Resume: Not connected.", False)
            return
        try:
            self.append_to_terminal("--- RESUMING MOVEMENT ---", True)
            resume_char = b'~'
            self.serial_connection.write(resume_char)
            self.append_to_terminal("SENT: ~ (Cycle Start / Resume)", True)
            self.status_bar.showMessage("Movement Resumed.")
        except Exception as e:
            self.append_to_terminal(f"ERROR sending Resume (~): {str(e)}", False)
            self.status_bar.showMessage(f"Resume Error: {str(e)}")
    # --- End of resume_movement function ---


    def refresh_ports(self):
        """Refreshes the list of available serial ports."""
        current_port = self.port_combo.currentText() # Remember selection
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        port_list = []
        found_current = False
        for port in sorted(ports, key=lambda p: p.device): # Sort ports
            # Add device and description if available for better identification
            desc = f" ({port.description})" if port.description and port.description != "n/a" else ""
            port_display_text = f"{port.device}{desc}"
            port_list.append(port_display_text)
            if port_display_text == current_port:
                 found_current = True

        if not port_list:
            self.port_combo.addItem("No ports found")
            self.port_combo.setEnabled(False) # Disable combo if empty
            self.status_bar.showMessage("No ports available")
        else:
            self.port_combo.addItems(port_list)
            # Try to restore previous selection
            if found_current and current_port:
                 self.port_combo.setCurrentText(current_port)
            self.port_combo.setEnabled(True) # Ensure enabled if ports found
            self.status_bar.showMessage("Ports refreshed")


    def toggle_connection(self):
        """Connects or disconnects the serial port."""
        if self.serial_connection is None:
            # --- Connect ---
            try:
                port_text = self.port_combo.currentText()
                # Extract only the port device name (e.g., COM3, /dev/ttyACM0)
                port = port_text.split(' ')[0]
                baud = int(self.baud_combo.currentText())

                if not port or "No ports" in port:
                    QMessageBox.critical(self, "Connection Error", "No valid serial port selected.")
                    return

                self.append_to_terminal(f"Attempting to connect to {port} at {baud} baud...")
                self.status_bar.showMessage(f"Connecting to {port}...")
                QApplication.processEvents() # Update UI

                # Establish serial connection
                self.serial_connection = serial.Serial(
                    port=port, baudrate=baud, timeout=1.0, write_timeout=1.0,
                    dsrdtr=False, rtscts=False, xonxoff=False
                )

                # Wait briefly for connection to stabilize
                # Some boards reset on connect (DTR toggle), requiring a pause
                time.sleep(1.5) # Adjust if needed based on board behavior

                if self.serial_connection.is_open:
                    self.connect_button.setText("Disconnect")
                    self.connect_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
                    self.status_bar.showMessage(f"Connected to {port} at {baud} baud")


                    # Start timer to read incoming serial data periodically
                    self.read_timer.start(100) # Read every 100ms
                    self.append_to_terminal(f"Successfully connected to {port}")

                    # Clear buffers and send initial commands
                    self.serial_connection.reset_input_buffer()
                    self.serial_connection.reset_output_buffer()
                    # Send newline to wake up / prompt Grbl/Marlin
                    self.serial_connection.write(b'\r\n')
                    time.sleep(0.2) # Allow time for welcome message/response

                    # Check status after connect
                    # Optional: Send $I or M115 to get firmware info
                    # self.send_and_wait("$I") # For Grbl
                    # self.send_and_wait("M115") # For Marlin/RepRapFirmware
                    # time.sleep(0.1)
                    self.send_and_wait("M114") # Get initial position

                    # Enable UI elements *after* initial commands sent
                    self.enable_ui_elements(True)

                else:
                    # This case should ideally not happen if Serial() succeeds without error
                    QMessageBox.critical(self, "Connection Error", f"Failed to open port {port}.")
                    self.serial_connection = None # Ensure it's reset
                    self.status_bar.showMessage("Connection Failed")


            except serial.SerialException as e:
                QMessageBox.critical(self, "Connection Error", f"Could not connect to {port}:\n{str(e)}")
                self.serial_connection = None
                self.status_bar.showMessage("Connection Failed")
                self.enable_ui_elements(False) # Ensure UI is disabled on failure
            except Exception as e:
                QMessageBox.critical(self, "Connection Error", f"An unexpected error occurred during connection:\n{str(e)}")
                self.serial_connection = None
                self.status_bar.showMessage("Connection Error")
                self.enable_ui_elements(False) # Ensure UI is disabled on failure

        else:
            # --- Disconnect ---
            try:
                self.append_to_terminal("Disconnecting...")
                self.read_timer.stop() # Stop reading serial data
                time.sleep(0.1) # Allow timer to fully stop

                if self.serial_connection and self.serial_connection.is_open:
                    # Optional: Send a command like M18 (disable motors) before closing?
                    # try:
                    #     self.serial_connection.write(b'M18\r\n')
                    #     time.sleep(0.1)
                    # except Exception: pass # Ignore errors during disconnect M18
                    self.serial_connection.close()
                    self.append_to_terminal("Serial connection closed.")
                else:
                    self.append_to_terminal("Serial connection was already closed or non-existent.")


            except Exception as e:
                self.append_to_terminal(f"Error during disconnect: {str(e)}", False)
            finally:
                # Ensure UI is updated regardless of errors during close
                self.serial_connection = None
                self.connect_button.setText("Connect")
                self.connect_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
                self.status_bar.showMessage("Disconnected")
                self.enable_ui_elements(False) # Disable controls


    def enable_ui_elements(self, connected):
        """Enables or disables UI elements based on connection status."""
        # Connection elements are enabled when *not* connected
        is_port_available = self.port_combo.count() > 0 and "No ports" not in self.port_combo.currentText()
        self.port_combo.setEnabled(not connected and is_port_available)
        self.baud_combo.setEnabled(not connected)
        self.refresh_button.setEnabled(not connected)

        # Command and control elements are enabled *when* connected
        self.command_input.setEnabled(connected)
        self.send_button.setEnabled(connected)
        self.halt_button.setEnabled(connected) # HALT button only active when connected
        self.feedrate_input.setEnabled(connected)
        self.step_input.setEnabled(connected)
        self.enable_motors_checkbox.setEnabled(connected)
        self.clear_terminal_button.setEnabled(True) # Always allow clearing terminal

        # Enable/disable common command buttons
        # Correctly access layout within the GroupBox
        common_commands_group = self.centralWidget().layout().itemAt(2).widget()
        if isinstance(common_commands_group, QGroupBox):
             cmd_layout_actual = common_commands_group.layout()
             if cmd_layout_actual: # Check if layout exists
                 for i in range(cmd_layout_actual.count()):
                     item = cmd_layout_actual.itemAt(i)
                     if item and item.widget() and isinstance(item.widget(), QPushButton):
                         item.widget().setEnabled(connected)

        # Enable/disable axis buttons (within the Movement Controls GroupBox)
        move_group = self.centralWidget().layout().itemAt(1).widget()
        if isinstance(move_group, QGroupBox):
            # Axis buttons are within the second layout (index 1) of the group's main layout
             axis_layout_container = move_group.layout().itemAt(1) # QVBoxLayout -> QGridLayout
             if axis_layout_container and axis_layout_container.layout():
                 axis_layout_actual = axis_layout_container.layout()
                 for i in range(axis_layout_actual.count()):
                     item = axis_layout_actual.itemAt(i)
                     if item and item.widget() and isinstance(item.widget(), QPushButton):
                          item.widget().setEnabled(connected)


    def eventFilter(self, obj, event):
        """Handles key presses (Up/Down arrows) in the command input for history."""
        if obj is self.command_input and event.type() == QEvent.KeyPress:
            key = event.key()

            if key == Qt.Key_Up and self.command_history:
                # Navigate up through history
                if self.history_position == -1: # If starting fresh, set to last item
                     self.history_position = len(self.command_history) -1
                else:
                     self.history_position = max(0, self.history_position - 1)

                if 0 <= self.history_position < len(self.command_history):
                    self.command_input.setText(self.command_history[self.history_position])
                    # Move cursor to end
                    self.command_input.setCursorPosition(len(self.command_input.text()))
                return True # Event handled

            elif key == Qt.Key_Down and self.command_history:
                # Navigate down through history
                if self.history_position < len(self.command_history) - 1:
                    self.history_position += 1
                    self.command_input.setText(self.command_history[self.history_position])
                else:
                    # If at the bottom or beyond, clear the input and reset position
                    self.history_position = len(self.command_history)
                    self.command_input.clear()
                # Move cursor to end
                self.command_input.setCursorPosition(len(self.command_input.text()))
                return True # Event handled

        # Call base class event filter for other events
        return super().eventFilter(obj, event)

    def send_command(self):
        """Sends the command from the input field."""
        if not self.serial_connection or not self.serial_connection.is_open:
            self.append_to_terminal("Cannot send: Not connected.", False)
            return

        command = self.command_input.text().strip() # Keep case sensitivity for commands like $X
        # command = self.command_input.text().strip().upper() # Or standardize to uppercase if preferred

        if command:
            # Add command to history (if different from last)
            if not self.command_history or self.command_history[-1] != command:
                self.command_history.append(command)
                # Limit history size
                if len(self.command_history) > 50: # Keep last 50 commands
                    self.command_history.pop(0)

            # Reset history position for next navigation
            self.history_position = len(self.command_history)

            # Send the command
            # Check for special characters like ~ before sending
            if command == "~":
                 self.resume_movement()
            # Add other special character handling if needed
            # elif command == "!":
            #      self.halt_movement()
            else:
                 self.send_and_wait(command)

            self.command_input.clear() # Clear input field after sending

    def read_serial_data(self):
        """Reads available data from the serial port and appends it to the terminal."""
        if not self.serial_connection or not self.serial_connection.is_open:
            return # Do nothing if not connected

        try:
            # Check if there's data waiting in the input buffer
            if self.serial_connection.in_waiting > 0:
                # Read all available data
                data = self.serial_connection.read(self.serial_connection.in_waiting)
                # Decode bytes to text, ignoring errors
                text = data.decode('utf-8', errors='ignore')
                if text:
                    # Append received text to the terminal (as non-command)
                    # Split by lines for potentially cleaner output if multiple lines received at once
                    for line in text.splitlines():
                         if line.strip(): # Avoid appending empty lines
                              self.append_to_terminal(line.strip(), False)

        except serial.SerialException as e:
            # Handle specific serial errors, e.g., device disconnected
            self.append_to_terminal(f"SERIAL ERROR: {str(e)} - Connection lost?", False)
            # Don't automatically disconnect here, let user handle it via button
            self.status_bar.showMessage(f"Serial Error: {str(e)}. Connection lost?")
            # Stop the timer if a serial error occurs
            self.read_timer.stop()
            # Visually update UI to reflect potential disconnect
            self.enable_ui_elements(False) # Disable controls
            self.connect_button.setText("Connect") # Reset button text
            self.connect_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
            self.serial_connection = None # Mark as disconnected internally


        except Exception as e:
            # Handle other unexpected errors during read
            self.append_to_terminal(f"ERROR reading serial data: {str(e)}", False)
            # Consider stopping timer or logging more details
            self.read_timer.stop()
            self.status_bar.showMessage(f"Read Error: {str(e)}")


    def append_to_terminal(self, text, is_command=False):
        """Appends text to the terminal output area with appropriate styling."""
        # Use HTML for basic coloring
        if is_command:
            # Green bold for sent commands
            self.terminal_output.append(f'<span style="color:#66bb6a; font-weight:bold;">&gt; {html.escape(text)}</span>') # Escaped command
        else:
            # Light gray for received data/messages
            escaped_text = html.escape(text)
            # Basic check for 'ok' or 'error' for highlighting
            if 'ok' in text.lower():
                 self.terminal_output.append(f'<span style="color:#81c784;">{escaped_text}</span>') # Lighter green for ok
            elif 'error' in text.lower():
                 self.terminal_output.append(f'<span style="color:#e57373; font-weight:bold;">{escaped_text}</span>') # Red for error
            else:
                 self.terminal_output.append(f'<span style="color:#bdbdbd;">{escaped_text}</span>') # Default light gray


        # Auto-scroll to the bottom
        scrollbar = self.terminal_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_terminal(self):
        """Clears the terminal output area."""
        self.terminal_output.clear()

    def closeEvent(self, event):
        """Ensures serial connection is closed when the window is closed."""
        print("Closing application...")
        if self.serial_connection and self.serial_connection.is_open:
            try:
                print("Stopping read timer...")
                self.read_timer.stop()
                print("Closing serial connection...")
                self.serial_connection.close()
                print("Serial connection closed.")
            except Exception as e:
                print(f"Error during closeEvent cleanup: {e}")
        event.accept() # Accept the close event


# --- Main execution block ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Apply a style for better looks if desired
    # app.setStyle('Fusion')
    window = CNCController()
    window.show()
    sys.exit(app.exec_())
