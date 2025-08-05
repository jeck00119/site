from enum import Enum

import cv2

try:
    from pypylon import pylon, genicam
except:
    pass

from services.camera.camera_model import CameraModel
from services.camera.implementation.fast_usb_camera import FastUSBCamera


class BaslerCameraSettings(Enum):
    EXPOSURE = 0
    EXPOSURE_AUTO = 1
    EXPOSURE_MODE = 2

    LINE_SELECTOR = 3
    LINE_MODE = 4
    LINE_SOURCE = 5
    LINE_INVERTER = 6
    USER_OUTPUT_SELECTOR = 7
    USER_OUTPUT_VALUE = 8

    TRIGGER_SELECTOR = 9
    TRIGGER_DELAY = 10
    TRIGGER_MODE = 11
    TRIGGER_SOURCE = 12
    TRIGGER_ACTIVATION = 13

    ACQUISITION_MODE = 14


basler_possibilities = {
    BaslerCameraSettings.LINE_SELECTOR.name: ['Line1', 'Line2', 'Line3']
}


class BaslerCamera(FastUSBCamera):
    DEFAULT_CAMERA_CONFIGURATION = {
        BaslerCameraSettings.EXPOSURE.name: 30000
    }

    def __init__(self, camera_model:CameraModel, config):
        data = self.DEFAULT_CAMERA_CONFIGURATION.copy()
        super().__init__(data=data, camera_model=camera_model)

    @classmethod
    def find_cameras(cls):
        return pylon.InstantCamera(pylon.TlFactory.GetInstance())

    def initialize(self):
        try:
            tlf = pylon.TlFactory.GetInstance()
            devices = tlf.EnumerateDevices()
            self._cap = pylon.InstantCamera(tlf.CreateDevice(devices[int(self._cameraIndex)]))
            self._cap.Open()
            # self._cap.MaxNumBuffer = 1
            self._cap.LineSelector.SetValue("Line3")
            self._cap.LineMode.SetValue("Input")
            #The following line only works in Output mode
            # self._cap.LineSource.SetValue('UserOutput2')
            self._cap.LineInverter.SetValue(True)
            self._cap.UserOutputSelector.SetValue('UserOutput2')
            self._cap.UserOutputValue.SetValue(False)

            self._cap.PixelFormat.SetValue('Mono8')

            self._cap.ExposureMode.SetValue('Timed')
            self._cap.ExposureAuto.SetValue('Off')
            self._cap.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        except Exception as e:
            print(e)
            print("Camera Basler initialization exception.")

    def release(self):
        if self._cap is not None:
            self._cap.StopGrabbing()
            self._cap.Close()

    def set(self, camera_property, value):

        if camera_property.upper() == BaslerCameraSettings.EXPOSURE.name:
            self._cap.ExposureTime.SetValue(value)
            return

        self._data[camera_property] = value

    def load_config(self, data: dict):
        for key, val in data.items():
            self._data[key] = val
            if BaslerCameraSettings.EXPOSURE.name == (key.upper()):
                if self._cap is not None:
                    self._cap.ExposureTime.SetValue(val)
                    continue

    def get_frame(self):
        try:
            result = self._cap.RetrieveResult(1500, pylon.TimeoutHandling_ThrowException)
        except genicam.GenericException as e:
            raise e
        if result.GrabSucceeded():
            image = self._converter.Convert(result)
            self._frame = image.GetArray()
        else:
            self._frame = self._default_frame


        self._frame = cv2.circle(self._frame, (round(self._frame.shape[1]/2), round(self._frame.shape[0]/2)), 25, (0, 0, 255))
        return self._frame

    def start(self):
        if not self._cap.IsGrabbing():
            self._cap.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    def stop(self):
        self._cap.StopGrabbing()
