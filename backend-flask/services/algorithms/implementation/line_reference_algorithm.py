import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from services.algorithms.implementation.dependencies.detection_calculations import Point


class LineReferenceAlgorithm(AbstractAlgorithm):
    def __init__(self, rho, theta, threshold, min_line_length, max_line_gap, reference_algorithm=None,
                 golden_position=None):
        super(LineReferenceAlgorithm, self).__init__(graphics=None, reference_algorithm=reference_algorithm,
                                                     golden_position=golden_position)
        self.rho = rho
        self.theta = theta
        self.threshold = threshold
        self.min_line_length = min_line_length
        self.max_line_gap = max_line_gap

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        proc_frame = frame.copy()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        kernel_size = (3, 3)
        frame = cv2.blur(frame, kernel_size)
        _, frame = cv2.threshold(frame, 220, 255, cv2.THRESH_BINARY)
        frame = cv2.Canny(frame, 50, 200)

        lines = cv2.HoughLinesP(frame, self.rho, self.theta * np.pi / 180, self.threshold, None, self.min_line_length,
                                self.max_line_gap)

        x = y = 0

        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(proc_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                x = x1 - x2 / 2
                y = y1 - y2 / 2

        reference = Point(x, y)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        self.algorithm_result.referencePoints = [reference]
        self.algorithm_result.imageRoi = proc_frame
        self.algorithm_result.data = self.compute_displacement(reference)
        self.algorithm_result.debugImages = [proc_frame, frame]
        return self.algorithm_result
