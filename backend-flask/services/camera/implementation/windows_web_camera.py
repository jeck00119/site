import cv2

from services.camera.camera_model import CameraModel, WebCamSettingsModel
from services.camera.implementation.web_camera import WebCamera


class WindowsWebCamera(WebCamera):
    def __init__(self, camera_model:CameraModel, camera_config_model):
        if camera_config_model:
            data = camera_config_model
        else:
            data = WebCamSettingsModel().model_dump()
            self._camera_id = camera_model.opencv_index_id
        super().__init__(camera_model=camera_model, data=data)

    @classmethod
    def find_cameras(cls):
        pass

    def initialize(self):
        from src.platform_utils import PlatformSpecificConfig
        
        # Setup Windows-specific environment
        PlatformSpecificConfig.setup_environment()
        
        # Use DirectShow backend for Windows
        self._cap = cv2.VideoCapture(self._camera_id, cv2.CAP_DSHOW)
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
        try:
            self._cap.set(cv2.CAP_PROP_FPS, 30)
        except cv2.error:
            pass

        ret, _ = self._cap.read()
        if ret:
            self._cap.read()
            self.initialized = True
        if self._cap.isOpened():
            super().initialize()
            return f"Camera initialized, cap opened."
        else:
            return f"Camera initialized, cap closed."
