import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi, detect_arucos


class ArucoDetectorAlgorithm(AbstractAlgorithm):
    dictionary_list = ["DICT_4x4_50", "DICT_4x4_100", "DICT_4x4_250", "DICT_4x4_1000",
                       "DICT_5x5_50", "DICT_5x5_100", "DICT_5x5_250", "DICT_5x5_1000",
                       "DICT_6x6_50", "DICT_6x6_100", "DICT_6x6_250", "DICT_6x6_1000",
                       "DICT_7x7_50", "DICT_7x7_100", "DICT_7x7_250", "DICT_7x7_1000"]

    def __init__(self, graphics, dictionary, reference_algorithm=None, golden_position=None):
        super().__init__(graphics, reference_algorithm=reference_algorithm, golden_position=golden_position)
        self.dictionary = dictionary

    @classmethod
    def from_dict(cls, algorithm, reference_algorithm=None, golden_position=None):
        return cls(graphics=algorithm["graphics"], dictionary=algorithm["dictionary"],
                   reference_algorithm=reference_algorithm, golden_position=golden_position)

    def execute(self, frame: np.ndarray):
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.algorithm_result = AlgorithmResult()

        roi, coordinates = crop_roi(frame, roi_offset=self.graphics[0]["offset"],
                                    roi_bound=self.graphics[0]["bound"], roi_rect=self.graphics[0]["rect"],
                                    rotation=self.graphics[0]["rotation"])
        arucos = self.detect_arucos(roi)

        if arucos:
            self.algorithm_result.data = True
        else:
            self.algorithm_result.data = False

        processed_img = cv2.rectangle(frame.copy(), (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]),
                                      (255, 0, 0), 5)
        processed_img[coordinates[1]:coordinates[3] - 1, coordinates[0]:coordinates[2] - 1] = roi

        self.algorithm_result.debugImages = [processed_img, frame, roi]
        self.algorithm_result.imageRoi = processed_img
        self.algorithm_result.data = {
            "numberOfArucos": len(arucos),
            "ids": [aruco["id"] for aruco in arucos]
        }

        return self.algorithm_result

    def detect_arucos(self, frame):
        arucos = detect_arucos(frame, dictionary=self.dictionary_list.index(self.dictionary))

        # arucos are sorted from left to right
        arucos_sorted = sorted(arucos, key=lambda k: k['x'])
        return arucos_sorted
