import numpy as np

from services.camera.implementation.interface_camera import CameraInterface


class DummyCamera(CameraInterface):
    def __init__(self, data):
        super(DummyCamera, self).__init__(data)

    def initialize(self):
        pass

    def is_opened(self):
        return True

    def runnable(self):
        pass

    def get_frame(self):
        return self._frame

    @staticmethod
    def get_frame_hard_trigger(fun_light):
        return np.zeros(shape=(3840, 2160, 3), dtype=np.uint8)

    def start(self):
        pass

    def stop(self):
        pass

    def release(self):
        pass

    def get(self, camera_property: int):
        return 0

    def set(self, camera_property: int, value):
        pass

    def load_and_set(self, data: dict):
        pass

    def status_check(self):
        pass

    def load_config(self, data: dict):
        pass

    def get_settings(self):
        return {}
