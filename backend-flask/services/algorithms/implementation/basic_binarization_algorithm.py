from copy import deepcopy

import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class BasicBinarizationAlgorithm(AbstractAlgorithm):
    def __init__(self, binary_threshold, binary_inverse, white_ratio, graphics, reference_algorithm=None,
                 golden_position=None):
        super().__init__(graphics, reference_algorithm=reference_algorithm, golden_position=golden_position)
        self.binary_threshold = binary_threshold
        self.binary_inverse = binary_inverse
        self.white_ratio = white_ratio

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()
        graphics_copy = deepcopy(self.graphics)

        height, width, channels = frame.shape

        # for roi in self.graphics:
        #     x = roi["roiBound"][0]
        #     y = roi["roiBound"][1]
        #     roi_width = roi["roiBound"][2]
        #     roi_height = roi["roiBound"][3]
        #
        #     if x < 0 or y < 0 or x + roi_width > width or y + roi_height > height:
        #         raise RoiOutOfImageBoundsException
        #
        # if channels != 3:
        #     raise InvalidImageDepthException(3, channels)

        if self.reference_algorithm is not None:
            ref_algorithm_result = self.reference_algorithm.execute(frame)
            if ref_algorithm_result.data is not None:
                self.algorithm_result.reference_debugImages = ref_algorithm_result.debugImages
                reference = ref_algorithm_result.referencePoint
                for roi in graphics_copy:
                    roi["bound"][0] += ref_algorithm_result.data.x
                    roi["bound"][1] += ref_algorithm_result.data.y

        roi, coordinates = crop_roi(frame, graphics_copy[0]["offset"], graphics_copy[0]["bound"],
                                    graphics_copy[0]["rect"], graphics_copy[0]["rotation"])

        for i, mask in enumerate(graphics_copy[0]["masks"]):
            masked = self.mask_region(roi, mask,
                                      color=(
                                          graphics_copy[0]["masksColors"][i][2], graphics_copy[0]["masksColors"][i][1],
                                          graphics_copy[0]["masksColors"][i][0]))
            roi = masked

        # cv2.imshow('result', roi)
        # cv2.waitKey(0)

        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        if self.binary_inverse > 0:
            _, roi = cv2.threshold(roi, self.binary_threshold, 255, cv2.THRESH_BINARY)
        else:
            _, roi = cv2.threshold(roi, self.binary_threshold, 255, cv2.THRESH_BINARY_INV)

        black = np.sum(roi == 0)
        white = np.sum(roi == 255)

        ratio = white / (white + black)

        if ratio > float(self.white_ratio):
            self.algorithm_result.data = {'pass': True}
        else:
            self.algorithm_result.data = {'pass': False}
        self.algorithm_result.imageRoi = roi
        self.algorithm_result.debugImages = [roi]

        return self.algorithm_result
