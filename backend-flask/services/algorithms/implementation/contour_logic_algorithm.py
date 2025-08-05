import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import adjust_gamma, crop_roi


class ContourLogicAlgorithm(AbstractAlgorithm):
    def __init__(self, lower_threshold, upper_threshold, kernel_dilate_size, dilate_iterations, kernel_erode_size,
                 erode_iterations, kernel_blur, part_area_min, part_area_max, gamma, line_size, graphics,
                 reference_algorithm=None, golden_position=None):
        super(ContourLogicAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                    golden_position=golden_position)

        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold

        self.gamma = gamma

        self.kernel_erode_size = kernel_erode_size
        self.erode_iterations = erode_iterations

        self.kernel_dilate_size = kernel_dilate_size
        self.dilate_iterations = dilate_iterations

        self.kernel_blur = kernel_blur

        self.part_area_min = part_area_min
        self.part_area_max = part_area_max
        self.line_size = line_size

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        roi, coordinates = crop_roi(frame, self.graphics[0]["offset"], self.graphics[0]["bound"],
                                    self.graphics[0]["rect"], self.graphics[0]["rotation"])

        roi = adjust_gamma(roi, float(self.gamma))
        color = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        thr, binary_roi = cv2.threshold(roi, self.lower_threshold, self.upper_threshold, cv2.THRESH_BINARY)

        if self.kernel_blur % 2 == 0:
            self.kernel_blur += 1

        binary_roi = cv2.GaussianBlur(binary_roi, (self.kernel_blur, self.kernel_blur), 0)
        kernel_dilate = np.ones((self.kernel_dilate_size, self.kernel_dilate_size), np.uint8)
        kernel_erode = np.ones((self.kernel_erode_size, self.kernel_erode_size), np.uint8)

        binary_roi = cv2.erode(binary_roi, kernel_erode, iterations=self.erode_iterations)
        binary_roi = cv2.dilate(binary_roi, kernel_dilate, iterations=self.dilate_iterations)

        contours, h = cv2.findContours(binary_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour_list = []

        for contour in contours:
            area = cv2.contourArea(contour)
            if self.part_area_min < area < self.part_area_max:
                contour_list.append(contour)
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(color, (x, y), (x + w, y + h), (0, 255, 0), self.line_size)

            cv2.drawContours(color, contour_list, -1, (255, 0, 255), self.line_size)

        processed_img = cv2.rectangle(frame, (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]),
                                      (255, 0, 0), 7)
        processed_img[coordinates[1]:coordinates[3] - 1, coordinates[0]:coordinates[2] - 1] = color

        self.algorithm_result.imageRoi = roi
        self.algorithm_result.data = {
            "cntNumber": len(contour_list)
        }
        self.algorithm_result.debugImages = [cv2.cvtColor(binary_roi, cv2.COLOR_GRAY2RGB), color]
        return self.algorithm_result
