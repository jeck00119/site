import cv2

from services.camera.camera_model import CameraModel, WebCamSettingsModel
from services.camera.implementation.web_camera import WebCamera, WebCameraSettings


class LinuxWebCamera(WebCamera):
    DEFAULT_CAMERA_CONFIGURATION = {
        WebCameraSettings.resolution.name: 5,
        WebCameraSettings.gain.name: 0,
        WebCameraSettings.pan.name: 0,
        WebCameraSettings.tilt.name: 0,
        WebCameraSettings.zoom.name: 0,
        WebCameraSettings.focus.name: 128,
        WebCameraSettings.auto_focus.name: 1,
        WebCameraSettings.brightness.name: 128,
        WebCameraSettings.contrast.name: 128,
        WebCameraSettings.saturation.name: 128,
        WebCameraSettings.sharpness.name: 128,
        WebCameraSettings.exposure.name: 1
    }

    GRAB_FRAME_TIME = 0.25

    def __init__(self, camera_model:CameraModel, camera_config_model):
        if camera_config_model:
            data = camera_config_model
        else:
            data = WebCamSettingsModel().model_dump()
            self._camera_id = camera_model.opencv_index_id
        super().__init__(camera_model=camera_model, data=data)


    def initialize(self):
        if self.initialized:
            return True, f"{self.name} a fost initializata!"

        self._cap = cv2.VideoCapture(self._cameraIndex, cv2.CAP_V4L2)
        # self._cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._data['resolution'][0])
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._data['resolution'][1])
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
        self._cap.set(cv2.CAP_PROP_FPS, 30)

        try:
            ret, _ = self._cap.read()
            if ret:
                self._cap.read()
                self.initialized = True
            if self._cap.isOpened():
                super(LinuxWebCamera, self).initialize()
                return True, f"{self.name} a fost initializata!"
            else:
                return False, f"{self.name} nu a fost initializata!"
        except cv2.error:
            return False, f"Eroare CV2: {self.name} nu a putut fi initializata!"

    # def set(self, camera_property, value):
    #     self._lock.acquire()
    #     self._data[camera_property] = value
    #     os.system(f'v4l2-ctl -d {self._cameraDeviceId} -c {self.settings[camera_property].name.lower()}={value}')
    #     self._lock.release()
