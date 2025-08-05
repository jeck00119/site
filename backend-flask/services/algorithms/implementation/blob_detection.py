import cv2 as cv2
import numpy as np
from skimage.segmentation import clear_border

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def set(self, x, y):
        self.x = x
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    # set the print_debuged text of the class
    def __str__(self):
        return "X: " + str(self.x) + " / Y: " + str(self.y)


class BlobDetection(AbstractAlgorithm):
    HELP = "Detects white blobs in the ROI" \
           + "You can enable/disable the area, circle, convexity and intertia. \n"

    def __init__(self, threshold_binarization, opening, closing,
                 ph1, ph2, area_enable,
                 circle_enable, conv_enable, inert_enable,
                 area_value, circle_value, conv_value,
                 inert_value, result_number, result_names,
                 graphics, golden_position=None, reference_algorithm=None):
        super().__init__(graphics=graphics, reference_algorithm=reference_algorithm, golden_position=golden_position)

        self.binary_threshold = threshold_binarization
        self.opening = opening
        self.closing = closing

        self.ph1 = ph1
        self.ph2 = ph2

        self.area_enable = area_enable
        self.circle_enable = circle_enable
        self.conv_enable = conv_enable
        self.inert_enable = inert_enable

        self.area_value = area_value
        self.circle_value = circle_value
        self.conv_value = conv_value
        self.inert_value = inert_value

        self.results_number = result_number
        self.results_names = result_names

        self.referenceAlgorithm = None
        self.goldenPosition = None

    @property
    def ph1(self):
        return self._ph1

    @ph1.setter
    def ph1(self, value):
        self._ph1 = value
        # and do smth else

    def execute(self, frame: np.ndarray):

        self.algorithmResult = AlgorithmResult()

        roi, coordinates = crop_roi(frame, self.graphics[0]["offset"], self.graphics[0]["bound"],
                                    self.graphics[0]["rect"], self.graphics[0]["rotation"])

        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        thr, binarized_roi = cv2.threshold(roi, self.binary_threshold, 255, cv2.THRESH_BINARY)

        kernel_33 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

        binarized_roi = cv2.dilate(binarized_roi, kernel_33, iterations=1)

        binarized_roi = clear_border(binarized_roi)
        kernel_33 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.closing, self.closing))
        binarized_roi = cv2.morphologyEx(binarized_roi, cv2.MORPH_CLOSE, kernel_33)
        kernel_33 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.opening, self.opening))
        binarized_roi = cv2.morphologyEx(binarized_roi, cv2.MORPH_OPEN, kernel_33)
        thr, binarized_roi = cv2.threshold(binarized_roi, 44, 255, cv2.THRESH_BINARY_INV)

        # Set up the detector with default parameters.
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = self.area_enable
        params.minArea = self.area_value
        params.filterByCircularity = self.circle_enable
        params.minCircularity = self.circle_value
        params.filterByConvexity = self.conv_enable
        params.minConvexity = self.conv_value
        params.filterByInertia = self.inert_enable
        params.minInertiaRatio = self.inert_value

        detector = cv2.SimpleBlobDetector_create(params)
        key_points = detector.detect(binarized_roi)
        listPoints = []
        roi = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)

        for key in key_points:
            cv2.putText(roi, f'{round(key.size, 2)}', (int(key.pt[0] - 20), int(key.pt[1] - 20)), cv2.FONT_HERSHEY_DUPLEX, 1.2,
                        (200, 200, 0), 3)

            if key.size > self.ph2 and key.size < self.ph2 + 35:
                listPoints.append(key.pt)

        # use blob detection algorithm as reference algorithm
        if len(listPoints) > 0:
            ref = Point(listPoints[0][0], listPoints[0][1])
        else:
            ref = Point(None, None)

        listPoints_in_origin_roi = {}
        listPoints_in_origin_frame = {}
        listPointsRef = {
            'c1p1x': 2.5,
            'c1p1y': 3.5,
            'c1p2x': 1.5,
            'c1p2y': 3
        }
        binarized_roi = cv2.cvtColor(binarized_roi, cv2.COLOR_GRAY2BGR)

        self.algorithmResult.data = listPointsRef
        self.algorithmResult.imageRoi = binarized_roi
        self.algorithmResult.debugImages = [roi, binarized_roi]
        self.algorithmResult.detailedDebug['points_in_origin_roi'] = listPoints_in_origin_roi
        self.algorithmResult.detailedDebug['points_in_origin_frame'] = listPoints_in_origin_frame

        return self.algorithmResult
