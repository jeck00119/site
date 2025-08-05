try:
    from pypylon import pylon
except:
    pass

from services.camera.implementation.interface_camera import CameraInterface


class FastUSBCamera(CameraInterface):
    def __init__(self, data, camera_model):
        super().__init__(data, camera_model=camera_model)

        self._converter = pylon.ImageFormatConverter()
        self._converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self._converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    def get_frame(self):
        pass

    def release(self):
        pass

    def initialize(self):
        pass

    def status_check(self):
        pass

    def load_config(self, data: dict):
        pass

    def get_settings(self):
        pass
