import collections

import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_exceptions import RoiOutOfImageBoundsException, \
    InvalidImageDepthException
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class MotionDetectionHistAlgorithm(AbstractAlgorithm):
    def __init__(self, history, variation_threshold, detect_shadows, detection_threshold, graphics,
                 reference_algorithm=None, golden_position=None):
        super().__init__(graphics, reference_algorithm=reference_algorithm, golden_position=golden_position)

        self.history = history
        self.variation_threshold = variation_threshold
        self.detect_shadows = detect_shadows
        self.detection_threshold = detection_threshold
        self.maxlen = 3

        self._back_sub = cv2.createBackgroundSubtractorMOG2(history=history, varThreshold=variation_threshold,
                                                            detectShadows=detect_shadows)
        self._hist_list = collections.deque(maxlen=self.maxlen)

    def execute(self, frame):
        self.algorithm_result = AlgorithmResult()

        height, width, channels = frame.shape

        for roi in self.graphics:
            x = roi["bound"][0]
            y = roi["bound"][1]
            roi_width = roi["bound"][2]
            roi_height = roi["bound"][3]

            if x < 0 or y < 0 or x + roi_width > width or y + roi_height > height:
                raise RoiOutOfImageBoundsException

        if channels != 3:
            raise InvalidImageDepthException(3, channels)

        roi, coordinates = crop_roi(frame, roi_offset=self.graphics[0]["offset"],
                                    roi_bound=self.graphics[0]["bound"],
                                    roi_rect=self.graphics[0]["rect"], rotation=self.graphics[0]["rotation"])

        fg_mask = self._back_sub.apply(roi)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

        ret, binarized_roi = cv2.threshold(fg_mask, 20, 255, cv2.THRESH_BINARY)
        n_white_pix = np.sum(binarized_roi == 255)

        ans = 1 if (n_white_pix > 300) else 0

        self._hist_list.append(ans)

        self.algorithm_result.data = {
            "motionAverage": None if (self._hist_list.maxlen != len(self._hist_list)) else sum(
                self._hist_list) / self._hist_list.maxlen
        }

        self.algorithm_result.imageRoi = binarized_roi
        self.algorithm_result.debugImages = [fg_mask, binarized_roi]

        return self.algorithm_result
