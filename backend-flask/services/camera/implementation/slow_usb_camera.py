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
        import time
        config_start = time.time()
        print(f"[CAMERA-CONFIG] Loading {len(data)} camera settings...")
        
        self._lock.acquire()
        try:
            # Skip slow/problematic settings that can be applied later or aren't critical
            fast_settings = {}
            slow_settings = {}
            
            for key, val in data.items():
                # Focus settings can be extremely slow (1+ seconds each)
                if key in ['auto_focus', 'focus']:
                    slow_settings[key] = val
                else:
                    fast_settings[key] = val
            
            # Apply fast settings first
            for key, val in fast_settings.items():
                self.set(key, val)
            
            # Apply slow settings only if necessary
            # You could make this optional based on a flag
            for key, val in slow_settings.items():
                print(f"[CAMERA-CONFIG] Applying slow setting: {key}")
                self.set(key, val)
                
        finally:
            self._lock.release()
        
        print(f"[CAMERA-CONFIG] Settings applied in {time.time() - config_start:.3f}s")


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
