import cv2
import numpy as np

# TLDR: it should find the start and end point of the clip starting from the around middle of it
from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


# expected work scenario given a line (two points)
# needs rework for one point +W,H calculate the middle start going down until it
# finds a black pixel starts going left/right from the Y = first black pixel found
# if no black pixel found at that high goes lower until
# black pixel is found OR difference of starting height and current height is more than Steep


class SteepDetectionAlgorithm(AbstractAlgorithm):
    def __init__(self, lower_threshold, upper_threshold, min_steep, graphics, reference_algorithm=None,
                 golden_position=None):
        super(SteepDetectionAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                      golden_position=golden_position)

        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold
        self.min_steep = min_steep
        self.height = 0
        self.width = 0
        self.result = 0

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        roi, coordinates = crop_roi(frame, roi_offset=self.graphics[0]["offset"],
                                    roi_bound=self.graphics[0]["bound"], roi_rect=self.graphics[0]["rect"],
                                    rotation=self.graphics[0]["rotation"])

        roi_color = roi.copy()
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        thr, binarized_roi = cv2.threshold(roi, self.lower_threshold, self.upper_threshold, cv2.THRESH_BINARY)
        self.height, self.width = roi.shape[:2]

        start_point = self._find_black(binarized_roi, (0, 0))

        stop_point = self._find_black(binarized_roi, (self.width - 1, 0))

        if start_point is not None or stop_point is not None:

            dif = abs(start_point - stop_point)

            font = cv2.FONT_HERSHEY_SIMPLEX
            size = 0.35
            text = "Difference : " + str(dif)

            textsize = cv2.getTextSize(text, font, size, 2)[0]
            textX = round((roi.shape[1] - textsize[0]) / 2)
            textY = round((roi.shape[0] + textsize[1]) / 2)

            if dif >= self.min_steep:
                color = (0, 0, 255)
            else:
                color = (0, 255, 0)

            cv2.putText(roi_color, text, (textX, round(textY / 2)), font, size, color, 2)
            cv2.circle(roi_color, (0, start_point), 5, color, 3)
            cv2.circle(roi_color, (self.width - 1, stop_point), 5, color, 3)

        processed_img = cv2.rectangle(frame, (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]),
                                     (255, 0, 0), 5)
        processed_img[coordinates[1]:coordinates[3] - 1, coordinates[0]:coordinates[2] - 1] = roi_color

        self.algorithm_result.image = roi
        self.algorithm_result.imageRoi = roi

        self.algorithm_result.data = {
            "startPoint": start_point,
            "stopPoint": stop_point
        }

        self.algorithm_result.debugImages = [processed_img, binarized_roi, roi_color]
        return self.algorithm_result

    def _find_black(self, roi, point):
        for y in range(point[1], self.height - 1):
            if roi[y, point[0]] == 0:
                return y
        return None
