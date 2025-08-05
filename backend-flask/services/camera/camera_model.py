from enum import Enum
from typing import Any

import cv2

from src.utils import generate_uid, CamelModel


class EnumCameraTypes(str, Enum):
    webcam_logi = "webcam_logi"
    basler_usb = "basler_usb"
    webcam_msft = "webcam_msft"


class CameraModel(CamelModel):
    uid: str = generate_uid(length=8)
    name: Any
    camera_type: EnumCameraTypes
    opencv_index_id: int = 0


class WebCameraSettings(Enum):
    resolution = 9999
    brightness = cv2.CAP_PROP_BRIGHTNESS
    contrast = cv2.CAP_PROP_CONTRAST
    saturation = cv2.CAP_PROP_SATURATION
    sharpness = cv2.CAP_PROP_SHARPNESS
    gain = cv2.CAP_PROP_GAIN
    auto_exposure = cv2.CAP_PROP_AUTO_EXPOSURE
    exposure = cv2.CAP_PROP_EXPOSURE
    pan = cv2.CAP_PROP_PAN
    tilt = cv2.CAP_PROP_TILT
    zoom = cv2.CAP_PROP_ZOOM
    focus = cv2.CAP_PROP_FOCUS
    auto_focus = cv2.CAP_PROP_AUTOFOCUS


class WebCamSettingsModel(CamelModel):
    uid: Any = generate_uid(length=8)
    name: str = f'webCam{uid}'
    camera_type: EnumCameraTypes = EnumCameraTypes.webcam_logi
    resolution: list = [640, 480]
    brightness: int = 128
    contrast: int = 128
    saturation: int = 128
    sharpness: int = 128
    gain: int = 0
    auto_exposure: int = 0
    exposure: int = 1
    pan: int = 0
    tilt: int = 0
    zoom: int = 0
    focus: int = 30
    auto_focus: int = 1


class BaslerSettingsModel(CamelModel):
    uid: Any = generate_uid(length=8)
    camera_type: str = "basler_usb"
    name: str = 'webCam'
    exposure: int = 30000


class EnumCameraControlsType(str, Enum):
    RANGE = 'range'
    DROPDOWN = 'dropdown'
    BOOL = 'bool'


class CameraControl():
    def __init__(self, name: str, type: str, values: list, currentValue: int, step: int):
        self.name = name
        self.type = type
        self.values = values
        self.currentValue = currentValue
        self.step = step


web_logi_controls = [
    CameraControl(name=WebCameraSettings.resolution.name,
                  type=EnumCameraControlsType.DROPDOWN,
                  values=[[640, 480], [1280, 720], [1920, 1080], [3840, 2160]],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.brightness.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.contrast.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.saturation.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.sharpness.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.gain.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.auto_exposure.name,
                  type=EnumCameraControlsType.BOOL,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.exposure.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[-12, 10],
                  currentValue=-6,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.pan.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.tilt.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.zoom.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.focus.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.auto_focus.name,
                  type=EnumCameraControlsType.BOOL,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
]

web_msft_controls = [
    CameraControl(name=WebCameraSettings.resolution.name,
                  type=EnumCameraControlsType.DROPDOWN,
                  values=[[640, 480], [1280, 720], [1920, 1080]],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.brightness.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.contrast.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.saturation.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.sharpness.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.gain.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.auto_exposure.name,
                  type=EnumCameraControlsType.BOOL,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.exposure.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[-12, 10],
                  currentValue=-6,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.pan.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.tilt.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.zoom.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.focus.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
    CameraControl(name=WebCameraSettings.auto_focus.name,
                  type=EnumCameraControlsType.BOOL,
                  values=[0, 256],
                  currentValue=126,
                  step=1, ).__dict__,
]

basler_controls = [
    CameraControl(name=WebCameraSettings.exposure.name,
                  type=EnumCameraControlsType.RANGE,
                  values=[35, 1000000],
                  currentValue=3000,
                  step=1, ).__dict__
]

camera_type_controls = {
    EnumCameraTypes.webcam_logi: web_logi_controls,
    EnumCameraTypes.basler_usb: basler_controls,
    EnumCameraTypes.webcam_msft: web_msft_controls
}

camera_type_default_settings = {
    EnumCameraTypes.webcam_logi: WebCamSettingsModel(),
    EnumCameraTypes.basler_usb: BaslerSettingsModel(),
    EnumCameraTypes.webcam_msft: WebCamSettingsModel()
}
