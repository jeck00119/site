import os
import threading
import time
import asyncio

import serial

from src.metaclasses.singleton import Singleton
from services.port_manager.port_manager import UnifiedUSBManager


class DatamanService(metaclass=Singleton):
    def __init__(self, port=None):
        self.port = port
        self.serial = None
        self.response_thread = None
        self.running = False
        self.running_lock = threading.Lock()
        self.data_lock = threading.Lock()
        self.data = ''
        self.port_manager = UnifiedUSBManager()

    def initialize(self):
        self.setup_serial()
        # self.start_response_thread()

    def setup_serial(self):
        """Setup serial connection using cross-platform USB device detection with validation."""
        try:
            # Use async method in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # If port was specified in constructor, validate it
            if self.port:
                validation_result = loop.run_until_complete(
                    self.port_manager.validate_port_for_device_type(self.port, 'dmc_readers')
                )
                print(f"DatamanService: {validation_result['error_message']}")
                
                if validation_result['is_valid']:
                    # Use the configured port if it's valid
                    device_port = validation_result['port']
                    self.port = device_port
                    self.serial = serial.Serial(port=device_port, timeout=1)
                    print(f"DatamanService: Connected to DMC reader at {device_port}")
                    loop.close()
                    return
                else:
                    print(f"DatamanService: Configured port validation failed - {validation_result['suggested_action']}")
            
            # Get DMC reader devices using centralized port manager
            dmc_devices = loop.run_until_complete(self.port_manager.get_dmc_reader_devices())
            
            if dmc_devices:
                # Use the first available DMC reader device
                device_port = dmc_devices[0]['device']
                self.port = device_port
                self.serial = serial.Serial(port=device_port, timeout=1)
                print(f"DatamanService: Connected to DMC reader at {device_port}")
            else:
                print("DatamanService: No DMC reader devices found")
                self.serial = None
            
            loop.close()
        except Exception as e:
            print(f"DatamanService: Failed to setup serial connection: {e}")
            self.serial = None

    def start_response_thread(self):
        self.running = True
        self.response_thread = threading.Thread(target=self.listen, args=())
        self.response_thread.start()

    def stop_response_thread(self):
        self.running_lock.acquire()
        self.running = False
        self.running_lock.release()

        if self.response_thread is not None:
            self.response_thread.join()
            self.response_thread = None

    def clear_data(self):
        self.data_lock.acquire()
        self.data = ''
        self.data_lock.release()

    def get_data(self):
        self.data_lock.acquire()
        data = self.data
        self.data_lock.release()
        return data

    def get_dmc_data(self):
        if self.serial.inWaiting() > 0:
            data = self.serial.readline().decode('utf-8')[:-2]
            return data

        return ''

    def reset_serial_buffer(self):
        self.serial.reset_input_buffer()

    def listen(self):
        if self.serial is None:
            return

        while True:
            self.running_lock.acquire()
            running = self.running
            self.running_lock.release()

            if not running:
                break

            if self.serial.inWaiting() > 0:
                current_dmc = self.serial.readline().decode('utf-8')[:-2]
                self.data_lock.acquire()
                if current_dmc != self.data:
                    self.data = current_dmc
                self.data_lock.release()

            time.sleep(0.01)

    def release(self):
        self.stop_response_thread()


if __name__ == '__main__':
    serial_service = DatamanService(port="COM4")
    serial_service.initialize()
