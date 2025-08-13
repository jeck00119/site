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
        import time
        from src.platform_utils import PlatformSpecificConfig
        
        init_start = time.time()
        
        # Setup Windows-specific environment
        PlatformSpecificConfig.setup_environment()
        
        # Use DirectShow backend for Windows (faster than default)
        # Alternative: Try cv2.CAP_MSMF (Media Foundation) which might be faster
        print(f"[CAMERA] Opening camera {self._camera_id} with DirectShow...")
        cap_start = time.time()
        self._cap = cv2.VideoCapture(self._camera_id, cv2.CAP_DSHOW)
        print(f"[CAMERA] VideoCapture opened in {time.time() - cap_start:.3f}s")
        
        # Set critical properties first
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for faster response
        
        # Set FPS for consistent frame rate
        try:
            self._cap.set(cv2.CAP_PROP_FPS, 30)
        except cv2.error:
            pass

        # Warm up the camera with a few reads
        warm_start = time.time()
        ret, _ = self._cap.read()
        if ret:
            self._cap.read()  # Second read to ensure camera is ready
            self.initialized = True
        print(f"[CAMERA] Camera warmup took {time.time() - warm_start:.3f}s")
        
        if self._cap.isOpened():
            super().initialize()
            print(f"[CAMERA] Total initialization took {time.time() - init_start:.3f}s")
            return f"Camera initialized, cap opened."
        else:
            return f"Camera initialized, cap closed."
