import cv2

from services.camera.camera_model import WebCameraSettings
from services.camera.implementation.slow_usb_camera import SlowUSBCamera


class WebCamera(SlowUSBCamera):
    def __init__(self, camera_model, data):
        super().__init__(camera_model=camera_model, data=data)
        self.settings = WebCameraSettings
        self.initialized = False

    def initialize(self):
        super().initialize()

    def release(self):
        if self._cap:
            self._cap.release()
        super().release()

    def update_last_frame(self):
        self._lock.acquire()
        ret, frame = self._cap.read()
        if ret:
            self._frame = frame
        else:
            self._frame = self._default_frame
        self._lock.release()

    def set(self, camera_property, value):
        if camera_property in self.settings.__members__:
            if camera_property == WebCameraSettings.resolution.name:
                try:
                    ret_width = self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, value[0])
                except cv2.error as e:
                    print(f"[ERROR] Resolution width {value[0]} (Exception: {e})")
                    ret_width = False

                try:
                    ret_height = self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, value[1])
                except cv2.error as e:
                    print(f"[ERROR] Resolution height {value[1]} (Exception: {e})")
                    ret_height = False

                if ret_width and ret_height:
                    print(f"[SUCCESS] Resolution set to {value[0]}x{value[1]}")
                    self._data[camera_property] = value
                else:
                    print(f"[FAILED] Resolution {value[0]}x{value[1]} (width: {ret_width}, height: {ret_height})")
                    self._data[camera_property] = value
            elif camera_property == WebCameraSettings.auto_exposure.name:
                try:
                    val = 0.75 if value >= 0.5 else 0.25
                    ret = self._cap.set(self.settings[camera_property].value, val)

                    if ret:
                        print(f"[SUCCESS] Auto exposure set to {val}")
                        self._data[camera_property] = val
                    else:
                        print(f"[FAILED] Auto exposure = {val} (camera rejected)")
                        self._data[camera_property] = val
                except cv2.error as e:
                    print(f"[ERROR] Auto exposure = {val} (Exception: {e})")
                    self._data[camera_property] = val
            else:
                try:
                    ret = self._cap.set(self.settings[camera_property].value, int(value))

                    if ret:
                        print(f"[SUCCESS] Camera property '{camera_property}' = {value}")
                        self._data[camera_property] = value
                    else:
                        print(f"[FAILED] Camera property '{camera_property}' = {value} (camera rejected)")
                        # Still update internal data - camera might have accepted it despite returning False
                        self._data[camera_property] = value
                        
                except cv2.error as e:
                    print(f"[ERROR] Camera property '{camera_property}' = {value} (Exception: {e})")
                    # Update internal data anyway
                    self._data[camera_property] = value
