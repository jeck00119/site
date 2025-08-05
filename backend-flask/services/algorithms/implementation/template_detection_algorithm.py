import cv2
import numpy as np
from imutils.object_detection import non_max_suppression

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from services.algorithms.implementation.dependencies.detection_calculations import Point
from src.utils import crop_roi


class TemplateDetectionAlgorithm(AbstractAlgorithm):
    def __init__(self, template_thresh, template_path, graphics, reference_algorithm=None, golden_position=None):
        super(TemplateDetectionAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                         golden_position=golden_position)
        self.template_thresh = template_thresh
        self.template_path = template_path

    def execute(self, frame):
        self.algorithm_result = AlgorithmResult()

        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        img_gray, coordinates = crop_roi(img_gray, self.graphics[0]["offset"], self.graphics[0]["bound"],
                                         self.graphics[0]["rect"], self.graphics[0]["rotation"])

        roi, coordinates = crop_roi(frame, self.graphics[0]["offset"], self.graphics[0]["bound"],
                                    self.graphics[0]["rect"], self.graphics[0]["rotation"])

        template = cv2.imread(self.template_path, 0)

        w, h = template.shape[::-1]

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

        loc = np.where(res >= self.template_thresh)

        middle_point = []

        rects = []

        for pt in zip(*loc[::-1]):
            rects.append((pt[0], pt[1], pt[0] + w, pt[1] + h))
            cv2.rectangle(roi, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)

        pick = non_max_suppression(np.array(rects))

        for (start_x, start_y, end_x, end_y) in pick:
            cv2.rectangle(roi, (start_x, start_y), (end_x, end_y), (255, 0, 0), 3)
            middle_point.append(Point(start_x + w / 2, start_y + h / 2))

        if len(middle_point) == 0:
            middle_point.append(Point(-1, -1))

        self.algorithm_result.referencePoints = [middle_point]
        self.algorithm_result.data = self.compute_displacement(middle_point[0])
        self.algorithm_result.imageRoi = frame
        self.algorithm_result.debugImages = [frame, template]
        return self.algorithm_result
