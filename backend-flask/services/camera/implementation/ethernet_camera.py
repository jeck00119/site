from services.camera.implementation.interface_camera import CameraInterface


class EthernetCamera(CameraInterface):
    def __init__(self, data):
        super(EthernetCamera, self).__init__(data)

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
