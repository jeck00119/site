import copy
import math

import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class ClipsShutAlgorithm(AbstractAlgorithm):
    def __init__(self, graphics, threshold, blur_kernel_size, blur_sigma, kernel_direction, kernel_size,
                 size_threshold, reference_algorithm=None, golden_position=None):
        super(ClipsShutAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                 golden_position=golden_position)
        self.threshold = threshold
        self.blur_kernel_size = blur_kernel_size
        self.blur_sigma = blur_sigma
        self.kernel_direction = kernel_direction
        self.kernel_size = kernel_size
        self.size_threshold = size_threshold

    def execute(self, frame: np.ndarray):
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

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (self.blur_kernel_size, self.blur_kernel_size), self.blur_sigma)
        # mask = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
        #                              self.adaptiveThresholdBlockSize, self.adaptiveThresholdConstant)

        mask = cv2.threshold(blur, self.threshold, 255, cv2.THRESH_BINARY)[1]

        if self.kernel_direction == "Horizontal":
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.kernel_size, 1))
        else:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, self.kernel_size))

        eroded = cv2.erode(cv2.bitwise_not(mask), kernel)
        dilated = cv2.dilate(eroded, kernel)

        contours = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[0]

        contours_sorted = sorted(contours, key=lambda c: self.contour_area(c), reverse=True)
        # contours.sort(key=lambda x: cv2.contourArea(x))

        size = 0

        if len(contours_sorted) != 0:
            cnt = contours_sorted[0]

            if self.kernel_direction == "Horizontal":
                pt1 = tuple(cnt[cnt[:, :, 0].argmin()][0])
                pt2 = tuple(cnt[cnt[:, :, 0].argmax()][0])
                pt2 = (pt2[0], pt1[1])
            else:
                pt1 = tuple(cnt[cnt[:, :, 1].argmin()][0])
                pt2 = tuple(cnt[cnt[:, :, 1].argmax()][0])
                pt2 = (pt1[0], pt2[1])

            size = round(math.sqrt((pt2[0] - pt1[0]) ** 2 + (pt2[1] - pt1[1])), 2)

            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(roi, (pt1[0], pt1[1]), 5, (0, 0, 255), -1)
            cv2.circle(roi, (pt2[0], pt2[1]), 5, (0, 0, 255), -1)
            cv2.putText(roi, str(size), (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        if size > self.size_threshold:
            passed = True
        else:
            passed = False

        processed_img = cv2.rectangle(frame, (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]), (255, 0, 0), 5)
        processed_img[coordinates[1]:coordinates[3] - 1, coordinates[0]:coordinates[2] - 1] = roi

        self.algorithm_result.imageRoi = roi
        self.algorithm_result.debugImages = [processed_img, roi, dilated]
        self.algorithm_result.data = {
            "pass": passed
        }
        self.algorithm_result.inspections_name = {
            f'{self.inspection_name}': passed,
        }

        return self.algorithm_result

    @staticmethod
    def contour_area(cnt):
        return cv2.contourArea(cnt)
