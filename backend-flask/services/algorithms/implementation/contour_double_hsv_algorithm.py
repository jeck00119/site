import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class ContourDoubleHSVAlgorithm(AbstractAlgorithm):
    def __init__(self, white_threshold, black_threshold, dilate_kernel, dilate_iterations, erode_kernel,
                 erode_iterations, blur_kernel, part_area_min, part_area_max, gamma, enable_inv_binarization,
                 white_lower_h, white_lower_s, white_lower_v, white_upper_h, white_upper_s, white_upper_v,
                 black_lower_h, black_lower_s, black_lower_v, black_upper_h, black_upper_s, black_upper_v, graphics,
                 reference_algorithm=None, golden_position=None):
        super(ContourDoubleHSVAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                        golden_position=golden_position)

        self.white_threshold = white_threshold
        self.black_threshold = black_threshold

        self.gamma = gamma

        self.erode_kernel = erode_kernel
        self.erode_iterations = erode_iterations

        self.dilate_kernel = dilate_kernel
        self.dilate_iterations = dilate_iterations

        self.blur_kernel = blur_kernel

        self.part_area_min = part_area_min
        self.part_area_max = part_area_max

        self.enable_inv_binarization = enable_inv_binarization

        self.white_lower_h = white_lower_h
        self.white_lower_s = white_lower_s
        self.white_lower_v = white_lower_v

        self.white_upper_h = white_upper_h
        self.white_upper_s = white_upper_s
        self.white_upper_v = white_upper_v

        self.black_lower_h = black_lower_h
        self.black_lower_s = black_lower_s
        self.black_lower_v = black_lower_v

        self.black_upper_h = black_upper_h
        self.black_upper_s = black_upper_s
        self.black_upper_v = black_upper_v

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        roi, coordinates = crop_roi(frame, roi_offset=self.graphics[0]["offset"],
                                    roi_bound=self.graphics[0]["bound"], roi_rect=self.graphics[0]["rect"],
                                    rotation=self.graphics[0]["rotation"])

        color = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        result, contour_list, binary_roi = self._process(color)

        cv2.drawContours(color, contour_list, -1, (255, 0, 255), 4)
        cv2.putText(color, str(result), (100, 100), cv2.FONT_HERSHEY_DUPLEX, 3, (255, 0, 0), 3)

        processed_img = cv2.rectangle(frame, (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]),
                                     (255, 0, 0), 5)
        processed_img[coordinates[1]:coordinates[3] - 1, coordinates[0]:coordinates[2] - 1] = color

        self.algorithm_result.data = {
            "result": result
        }
        self.algorithm_result.imageRoi = cv2.cvtColor(binary_roi, cv2.COLOR_GRAY2RGB)
        self.algorithm_result.debugImages = [processed_img, cv2.cvtColor(binary_roi, cv2.COLOR_GRAY2RGB), color]
        return self.algorithm_result

    def _process(self, color):
        lower_hsv = np.array([self.white_lower_h, self.white_lower_s, self.white_lower_v])
        upper_hsv = np.array([self.white_upper_h, self.white_upper_s, self.white_upper_v])

        hsv = cv2.cvtColor(color, cv2.COLOR_RGB2HSV)
        mask1 = cv2.inRange(hsv, lower_hsv, upper_hsv)

        contour_list = self._find_contours(mask1, color)

        if len(contour_list) > 0:
            return 1, contour_list, mask1
        else:
            lower_hsv1 = np.array([self.black_lower_h, self.black_lower_s, self.black_lower_v])
            upper_hsv1 = np.array([self.black_upper_h, self.black_upper_s, self.black_upper_v])

            mask2 = cv2.inRange(hsv, lower_hsv1, upper_hsv1)

            contour_list = self._find_contours(mask2, color)
            if len(contour_list) > 0:
                return 0, contour_list, mask2
            else:
                return -1, [], mask2

    def _pre_process(self, binary_roi):
        kernel_dilate = np.ones((self.dilate_kernel, self.dilate_kernel), np.uint8)
        kernel_erode = np.ones((self.erode_kernel, self.erode_kernel), np.uint8)

        if self.blur_kernel % 2 == 0:
            self.blur_kernel += 1
        binary_roi = cv2.GaussianBlur(binary_roi, (self.blur_kernel, self.blur_kernel), 0)
        binary_roi = cv2.erode(binary_roi, kernel_erode, iterations=self.erode_iterations)
        binary_roi = cv2.dilate(binary_roi, kernel_dilate, iterations=self.dilate_iterations)
        return binary_roi

    def _find_contours(self, binary_roi, color):
        contours, h = cv2.findContours(binary_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        contour_list = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.part_area_min < area < self.part_area_max:
                contour_list.append(contour)
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(color, (x, y), (x + w, y + h), (0, 255, 0), 5)
        return contour_list
