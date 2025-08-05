import copy

import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class BrightnessAveragingAlgorithm(AbstractAlgorithm):
    def __init__(self, bottom_threshold, upper_threshold, percentage_threshold, graphics, reference_algorithm=None,
                 golden_position=None):
        super(BrightnessAveragingAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                           golden_position=golden_position)
        self.bottom_threshold = bottom_threshold
        self.upper_threshold = upper_threshold
        self.percentage_threshold = percentage_threshold

    def execute(self, frame):
        self.algorithm_result = AlgorithmResult()

        graphics_copy = copy.deepcopy(self.graphics)

        if self.reference_algorithm is not None:
            algorithm_result = self.reference_algorithm.execute(frame)
            if algorithm_result.data is not None:
                reference = algorithm_result.referencePoint
                if reference.x is not None:
                    for roi in graphics_copy:
                        roi["bound"][0] += reference.x
                        roi["bound"][1] += reference.y

        roi, coordinates = crop_roi(frame, roi_offset=graphics_copy[0]["offset"],
                                    roi_bound=graphics_copy[0]["bound"], roi_rect=graphics_copy[0]["rect"],
                                    rotation=graphics_copy[0]["rotation"])

        roi = roi[:, :, :3]

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        between_thresholds_index = np.where(np.logical_and(gray >= self.bottom_threshold, gray <= self.upper_threshold))

        total_pixels_number = roi.shape[0] * roi.shape[1]
        between_thresholds = between_thresholds_index[0].shape[0]

        p = (between_thresholds * 100) / total_pixels_number

        if p > self.percentage_threshold:
            pass_value = True
        else:
            pass_value = False

        if pass_value:
            color = (0, 255, 0)
            res = 'ok'
        else:
            color = (0, 0, 255)
            res = 'nok'

        org = (0, 30)

        roi = cv2.putText(roi, res, org, cv2.FONT_HERSHEY_SIMPLEX,
                          1, color, 2, cv2.LINE_AA)

        # Use logging instead of print for better debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Brightness percentage: {p}")

        for i in range(between_thresholds_index[0].shape[0]):
            roi[between_thresholds_index[0][i], between_thresholds_index[1][i]] = [0, 255, 0]

        avg = np.mean(gray)

        self.algorithm_result.imageRoi = roi
        self.algorithm_result.debugImages = [roi]
        self.algorithm_result.data = {
            "average": avg
        }

        return self.algorithm_result
