import time
from abc import abstractmethod
from threading import Thread, Event, Lock

from services.camera.implementation.interface_camera import CameraInterface


class SlowUSBCamera(CameraInterface):
    def __init__(self, data, camera_model):
        super().__init__(camera_model=camera_model, data=data)
        self._grab_thread = None
        self._lock = Lock()
        self.cameraSettingsThread = None

    def get_frame(self):
        return self._frame

    @abstractmethod
    def update_last_frame(self):
        pass

    def init_grab_thread(self):
        self._grab_thread = CameraThread(self.update_last_frame)
        self._grab_thread.start()

    def release_grab_thread(self):
        if self._grab_thread:
            self._grab_thread.stop()
            self._grab_thread.join()

    def initialize(self):
        self.init_grab_thread()

    def release(self):
        self.release_grab_thread()

    def load_config(self, data: dict):
        self._lock.acquire()
        for key, val in data.items():
            self.set(key, val)
        self._lock.release()


class CameraThread(Thread):
    def __init__(self, update_frame):
        super().__init__()
        self._running = Event()
        self.update_frame = update_frame
        self.getFramesFlag = True
        self.flagLock = Lock()

    def run(self) -> None:
        while not self._running.is_set():
            self.flagLock.acquire()
            flag = self.getFramesFlag
            self.flagLock.release()

            if flag:
                self.update_frame()

            time.sleep(0.03)

    def stop(self):
        self._running.set()

    def set_frames_flag(self, value: bool):
        self.flagLock.acquire()
        self.getFramesFlag = value
        self.flagLock.release()
