from abc import abstractmethod

import cv2
import numpy as np

from services.camera.camera_model import CameraModel


class CameraInterface():
    def __init__(self, data, camera_model:CameraModel):
        super().__init__()
        self.type = camera_model.camera_type
        self._name = camera_model.name
        self._cap = None
        self._cameraIndex = camera_model.opencv_index_id
        self._default_frame = np.zeros(shape=(640, 700, 3), dtype="uint8")
        cv2.putText(self._default_frame, "PLEASE WAIT...", (30, 320), cv2.FONT_HERSHEY_DUPLEX, 2,
                    (0, 0, 255), 3)
        self._frame = self._default_frame
        self._data = data

    @abstractmethod
    def get_frame(self):
        pass

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def status_check(self):
        pass

    @abstractmethod
    def load_config(self, data: dict):
        pass

    @abstractmethod
    def get_settings(self):
        pass

    def get_settings_list(self):
        return []

    def wait_for_settings(self):
        pass

    @property
    def name(self):
        return self._name

    def get_default_frame(self):
        return self._default_frame

    def get_data(self):
        return self._data

    def get_data_property(self, camera_property):
        try:
            return self._data[camera_property]
        except KeyError:
            return -1

    def get(self, camera_property):
        if camera_property == "RESOLUTION":
            width = self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

            res = [int(width), int(height)]

            for i in range(len(self.RESOLUTIONS)):
                if self.RESOLUTIONS[i] == res:
                    return i

            # 5 is 640 x 480 resolution (check self.RESOLUTIONS)
            return 5
        else:
            return self._cap.get(self.get_settings()[camera_property].value)

    def set(self, camera_property, value):
        pass
