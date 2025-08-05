import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class ColorAveragingAlgorithm(AbstractAlgorithm):
    def __init__(self, bottom_threshold, upper_threshold, graphics, reference_algorithm=None, golden_position=None):
        super(ColorAveragingAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                      golden_position=golden_position)
        self.bottom_threshold = bottom_threshold
        self.upper_threshold = upper_threshold

    def execute(self, frame):
        self.algorithm_result = AlgorithmResult()

        roi, coordinates = crop_roi(frame, roi_offset=self.graphics[0]["offset"],
                                    roi_bound=self.graphics[0]["bound"], roi_rect=self.graphics[0]["rect"],
                                    rotation=self.graphics[0]["rotation"])

        for i, mask in enumerate(self.graphics[0]["masks"]):
            masked = self.mask_region(roi, mask,
                                      color=(
                                          self.graphics[0]["masksColors"][i][2], self.graphics[0]["masksColors"][i][1],
                                          self.graphics[0]["masksColors"][i][0]))
            roi = masked

        cv2.imshow('result', roi)
        cv2.waitKey(0)

        blue_avg = np.mean(roi[:, :, 0])
        green_avg = np.mean(roi[:, :, 1])
        red_avg = np.mean(roi[:, :, 2])

        color = np.ones(shape=roi.shape, dtype=np.uint8)

        color = color * np.array([int(blue_avg), int(green_avg), int(red_avg)])

        self.algorithm_result.imageRoi = roi
        self.algorithm_result.debugImages = [roi, color]
        self.algorithm_result.data = {
            "blueAverage": blue_avg,
            "greenAverage": green_avg,
            "redAverage": red_avg
        }

        return self.algorithm_result
