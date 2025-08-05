import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_exceptions import RoiOutOfImageBoundsException, \
    InvalidImageDepthException
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from services.algorithms.implementation.dependencies.detection_calculations import Point
from src.utils import crop_roi


class VerticalLinePositionAlgorithm(AbstractAlgorithm):
    def __init__(self, binary_threshold, vertical_start, vertical_stop, graphics, reference_algorithm=None,
                 golden_position=None):
        super(VerticalLinePositionAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                            golden_position=golden_position)
        self.binary_threshold = binary_threshold

        self.vertical_start = vertical_start
        self.vertical_stop = vertical_stop

    def execute(self, frame: np.ndarray):
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

        frame, coordinates = crop_roi(frame, self.graphics[0]["offset"], self.graphics[0]["bound"],
                                      self.graphics[0]["rect"], self.graphics[0]["rotation"])

        height, width, channels = frame.shape

        frame_color = frame.copy()

        ## BINARIZARE
        binarized_roi = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.binary_threshold == 255:
            ret, binarized_roi = cv2.threshold(binarized_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            ret, binarized_roi = cv2.threshold(binarized_roi, self.binary_threshold, 255, cv2.THRESH_BINARY)
        ## BINARIZARE

        if self.vertical_start == 0:
            self.vertical_start = 50

        if self.vertical_stop == 0:
            self.vertical_stop = height - 50

        vertical_one_found = self.find_x(self.vertical_start, binarized_roi, frame_color)
        vertical_two_found = self.find_x(self.vertical_stop, binarized_roi, frame_color)

        dist_x = vertical_one_found[0]
        vertical_angle = 1234
        try:
            vertical_angle = self.calculate_angle(vertical_one_found, vertical_two_found)
        except:
            pass

        cv2.putText(frame_color, "Angle:" + str(vertical_angle), (5, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 0, 0), 2)
        cv2.putText(frame_color, "Distance:" + str(dist_x), (5, 60), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 0, 0), 2)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        reference = Point(vertical_one_found[0], vertical_one_found[1])

        self.algorithm_result.referencePoints = [reference]
        self.algorithm_result.data = self.compute_displacement(reference)
        self.algorithm_result.imageRoi = frame
        self.algorithm_result.debugImages = [frame_color, binarized_roi]

        return self.algorithm_result

    def calculate_angle(self, p1, p2):
        m1 = self.calculate_slope(p1, p2)
        return np.arctan(m1) * 180 / np.pi

    @staticmethod
    def calculate_slope(p1, p2):
        return (p2[1] - p1[1]) / (p2[0] - p1[0])

    @staticmethod
    def find_x(py, roi, frame):
        px = -1
        height, width = roi.shape[:2]

        for i in range(width - 10, 0, -1):
            cv2.circle(frame, (i, py), 2, (255, 0, 0), 5)
            if roi[py, i] == 0:
                px = i
                break
        return px, py
