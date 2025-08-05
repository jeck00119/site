import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from services.algorithms.implementation.dependencies.detection_calculations import Point
from src.utils import crop_roi


class ClipsReferenceAlgorithm(AbstractAlgorithm):
    def __init__(self, blur_kernel_size, blur_sigma, adaptive_threshold_block_size,
                 adaptive_threshold_constant, kernel_direction, kernel_size, closing_kernel, min_contour_area, graphics,
                 reference_algorithm=None, golden_position=None):
        super(ClipsReferenceAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                      golden_position=golden_position)
        self.blur_kernel_size = blur_kernel_size
        self.blur_sigma = blur_sigma
        self.adaptive_threshold_block_size = adaptive_threshold_block_size
        self.adaptive_threshold_constant = adaptive_threshold_constant
        self.min_contour_area = min_contour_area
        self.kernel_direction = kernel_direction
        self.kernel_size = kernel_size
        self.closing_kernel = closing_kernel

        self.count = 0

    def execute(self, frame):
        self.algorithm_result = AlgorithmResult()

        roi, coordinates = crop_roi(frame, self.graphics[0]["offset"], self.graphics[0]["bound"],
                                    self.graphics[0]["rect"], self.graphics[0]["rotation"])

        left_pt, right_pt, out = self.find_bmu_references(roi)

        if left_pt is not None:
            ref = Point(int(left_pt[0]), int(left_pt[1]))
        else:
            ref = Point(None, None)

        self.algorithm_result.referencePoints = [ref]
        self.algorithm_result.data = self.compute_displacement(ref)
        self.algorithm_result.imageRoi = out
        self.algorithm_result.debugImages = [roi, out]

        return self.algorithm_result

    def find_bmu_references(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (self.blur_kernel_size, self.blur_kernel_size),
                                self.blur_sigma)
        mask = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                     self.adaptive_threshold_block_size, self.adaptive_threshold_constant)

        if self.kernel_direction == "Horizontal":
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.kernel_size, 1))
        else:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, self.kernel_size))

        eroded = cv2.erode(cv2.bitwise_not(mask), kernel)
        dilated = cv2.dilate(eroded, kernel)

        remove = np.zeros(dilated.shape, dtype=np.uint8)

        contours = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        for c in contours:
            area = cv2.contourArea(c)
            if area > self.min_contour_area:
                cv2.drawContours(remove, [c], -1, 255, -1, 1)

        remove = cv2.bitwise_and(remove, dilated)

        closing = cv2.morphologyEx(remove, cv2.MORPH_CLOSE,
                                   kernel=np.ones(shape=(self.closing_kernel, self.closing_kernel), dtype=np.uint8))

        contours = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]

        # contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)
        contours = list(contours)
        contours_sorted = self.sort_contours(contours)[0]

        left_most_pt = (0, 0)
        right_most_pt = (0, 0)

        if len(contours_sorted) != 0:
            cnt = contours_sorted[-1]

            cv2.drawContours(img, cnt, -1, (0, 255, 0), 2)

            left_most_pt = tuple(cnt[cnt[:, :, 0].argmin()][0])
            right_most_pt = tuple(cnt[cnt[:, :, 0].argmax()][0])

            cv2.circle(img, (left_most_pt[0], left_most_pt[1]), 5, (0, 0, 255), -1)
            cv2.circle(img, (right_most_pt[0], right_most_pt[1]), 5, (0, 0, 255), -1)

        return left_most_pt, right_most_pt, closing

    @staticmethod
    def get_contour_precedence(contour, cols):
        tolerance_factor = 10
        origin = cv2.boundingRect(contour)
        return ((origin[1] // tolerance_factor) * tolerance_factor) * cols + origin[0]

    @staticmethod
    def sort_contours(contours):
        reverse = False
        i = 1

        bounding_boxes = [cv2.boundingRect(c) for c in contours]
        if len(bounding_boxes) != 0:
            (contours, boundingBoxes) = zip(*sorted(zip(contours, bounding_boxes),
                                                    key=lambda b: b[1][i], reverse=reverse))

        return contours, bounding_boxes
