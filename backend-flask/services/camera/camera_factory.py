from src.platform_utils import is_windows, is_linux
from services.camera.camera_model import EnumCameraTypes, CameraModel
from services.camera.implementation.basler_camera import BaslerCamera
from services.camera.implementation.linux_web_camera import LinuxWebCamera
from services.camera.implementation.windows_web_camera import WindowsWebCamera


class CameraFactory:
    @staticmethod
    def create_camera(camera_model: CameraModel, camera_config=None):
        """Create camera instance based on platform and camera type."""
        
        if camera_model.camera_type == EnumCameraTypes.webcam_logi or camera_model.camera_type == EnumCameraTypes.webcam_msft:
            if is_linux():
                return LinuxWebCamera(camera_model, camera_config)
            elif is_windows():
                return WindowsWebCamera(camera_model, camera_config)
            else:
                # Fallback to Windows implementation for unknown platforms
                return WindowsWebCamera(camera_model, camera_config)
        elif camera_model.camera_type == EnumCameraTypes.basler_usb:
            return BaslerCamera(camera_model, camera_config)
        else:
            return None
