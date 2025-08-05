import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class ConformalHSVAlgorithm(AbstractAlgorithm):
    def __init__(self, graphics, min_h=0, min_s=0, min_v=0, max_h=255, max_s=255, max_v=255, reference_algorithm=None,
                 golden_position=None):
        super(ConformalHSVAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                    golden_position=golden_position)
        self.min_h = min_h
        self.min_s = min_s
        self.min_v = min_v
        self.max_h = max_h
        self.max_s = max_s
        self.max_v = max_v

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        roi, coordinates = crop_roi(frame, self.graphics[0]["offset"], self.graphics[0]["bound"],
                                    self.graphics[0]["rect"], self.graphics[0]["rotation"])

        blur_roi = cv2.medianBlur(roi, 3)
        hsv_roi = cv2.cvtColor(blur_roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, (self.min_h, self.min_s, self.min_v), (self.max_h, self.max_s, self.max_v))

        result = cv2.bitwise_and(roi, roi, mask=mask)

        processed_img = cv2.rectangle(frame, (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]),
                                     (255, 0, 0), 7)
        processed_img[coordinates[1]:coordinates[3] - 1, coordinates[0]:coordinates[2] - 1] = result

        self.algorithm_result.imageRoi = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        self.algorithm_result.image = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        self.algorithm_result.debugImages = [processed_img, result]
        return self.algorithm_result
