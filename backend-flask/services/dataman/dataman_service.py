import os
import threading
import time

import serial

from src.metaclasses.singleton import Singleton


class DatamanService(metaclass=Singleton):
    def __init__(self, port=None):
        self.port = port
        self.serial = None
        self.response_thread = None
        self.running = False
        self.running_lock = threading.Lock()
        self.data_lock = threading.Lock()
        self.data = ''

    def initialize(self):
        self.setup_serial()
        # self.start_response_thread()

    def setup_serial(self):
        directory_path = "/dev/serial/by-id"
        files = [f for f in os.listdir(directory_path) if "cognex" in f]
        if len(files) != 0:
            self.serial = serial.Serial(port=f'{directory_path}/{files[0]}', timeout=1)

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
