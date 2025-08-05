import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_exceptions import ReferenceNotFound
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from services.algorithms.implementation.dependencies.detection_calculations import Point
from src.utils import crop_roi


class ContourGravityCenterAlgorithm(AbstractAlgorithm):
    def __init__(self, gaussian_blur_kernel_size, gaussian_blur_sigma, bin_low_threshold, closing_kernel_size,
                 invert_thresholding,  graphics, reference_algorithm=None, golden_position=None):
        super(ContourGravityCenterAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                            golden_position=golden_position)
        self.gaussian_blur_kernel_size = gaussian_blur_kernel_size
        self.gaussian_blur_sigma = gaussian_blur_sigma
        self.bin_low_threshold = bin_low_threshold
        self.closing_kernel_size = closing_kernel_size
        self.invert_thresholding = invert_thresholding

    def execute(self, frame):
        roi, _ = crop_roi(frame, self.graphics[0]["offset"], self.graphics[0]["bound"],
                          self.graphics[0]["rect"], self.graphics[0]["rotation"])

        for i, mask in enumerate(self.graphics[0]["masks"]):
            masked = self.mask_region(roi, mask,
                                      color=(
                                          self.graphics[0]["masksColors"][i][2], self.graphics[0]["masksColors"][i][1],
                                          self.graphics[0]["masksColors"][i][0]))
            roi = masked

        cv2.imshow('result', roi)
        cv2.waitKey(0)

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (self.gaussian_blur_kernel_size, self.gaussian_blur_kernel_size),
                                self.gaussian_blur_sigma)

        if self.invert_thresholding:
            method = cv2.THRESH_BINARY_INV
        else:
            method = cv2.THRESH_BINARY

        ret, thresh = cv2.threshold(blur, self.bin_low_threshold, 255, method)

        kernel = np.ones(shape=(self.closing_kernel_size, self.closing_kernel_size), dtype=np.uint8)
        closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        contours = list(contours)
        contours.sort(key=lambda c: cv2.contourArea(c))

        x = None
        y = None

        x1 = y1 = 0
        if len(contours) != 0:
            cv2.drawContours(roi, contours[-1], -1, (0, 0, 255), 3)
            M = cv2.moments(contours[-1])
            if M["m00"] != 0:
                x = float(M["m10"] / M["m00"]) + float(self.graphics[0]["bound"][0])
                y = float(M["m01"] / M["m00"]) + float(self.graphics[0]["bound"][1])
                x1 = float(M["m10"] / M["m00"])
                y1 = float(M["m01"] / M["m00"])

        ref_in_roi = Point(x1, y1)

        if x is not None:
            ref_in_frame = Point(x, y)
            cv2.circle(roi, (int(x), int(y)), 1, (255, 0, 0), 4)
        else:
            ReferenceNotFound

        golden_diff = self.compute_displacement(ref_in_frame)

        self.algorithm_result = AlgorithmResult()
        self.algorithm_result.referencePoints = [ref_in_frame]
        self.algorithm_result.data = golden_diff
        self.algorithm_result.imageRoi = roi
        self.algorithm_result.debugImages = [roi]
        self.algorithm_result.debugPoints = {
            'ref_in_roi_origin': ref_in_roi,
            'ref_in_frame_origin': ref_in_frame,
            'golden_difference': Point(golden_diff.x, golden_diff.y)
        }

        return self.algorithm_result
