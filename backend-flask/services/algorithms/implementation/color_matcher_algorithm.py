import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi, hex_to_rgb


class ColorMatcherAlgorithm(AbstractAlgorithm):
    def __init__(self, graphics, expected_color_code="#000000", threshold=30, reference_algorithm=None,
                 golden_position=None):
        super().__init__(graphics, reference_algorithm=reference_algorithm, golden_position=golden_position)
        self.threshold = threshold
        self.expected_color_code = expected_color_code

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        roi, coordinates = crop_roi(frame, roi_offset=self.graphics[0]["offset"],
                                    roi_bound=self.graphics[0]["bound"], roi_rect=self.graphics[0]["rect"],
                                    rotation=self.graphics[0]["rotation"])
        color_code = self.detect_color_code(roi)

        color_code_tuple = hex_to_rgb(self.expected_color_code)

        match = self.matching_colors(color_code, color_code_tuple)

        processed_img = cv2.rectangle(frame, (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]), (255, 0, 0), 5)
        processed_img[coordinates[1]:coordinates[3] - 1, coordinates[0]:coordinates[2] - 1] = roi

        self.algorithm_result.data = {
            "match": match
        }

        self.algorithm_result.imageRoi = roi
        self.algorithm_result.debugImages = [processed_img, roi]

        return self.algorithm_result

    def detect_color_code(self, frame: np.ndarray):
        blue_channel = cv2.calcHist([frame], [0], None, [256], [0, 256])
        green_channel = cv2.calcHist([frame], [1], None, [256], [0, 256])
        red_channel = cv2.calcHist([frame], [2], None, [256], [0, 256])

        blue_max = np.argmax(blue_channel)
        green_max = np.argmax(green_channel)
        red_max = np.argmax(red_channel)

        return blue_max, green_max, red_max

    def matching_colors(self, code_1, code_2):
        diff = abs(code_1[0] - code_2[0]) + abs(code_1[1] - code_2[1]) + abs(code_1[2] - code_2[2])
        if diff < self.threshold:
            return True
        else:
            return False
