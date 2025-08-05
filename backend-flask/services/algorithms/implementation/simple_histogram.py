import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class SimpleHistogramAlgorithm(AbstractAlgorithm):
    def __init__(self, graphics, reference_algorithm=None,
                 golden_position=None):
        super().__init__(graphics=graphics, reference_algorithm=reference_algorithm, golden_position=golden_position)


    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        roi, coordinates = crop_roi(frame, self.graphics[0]["offset"], self.graphics[0]["bound"],
                                    self.graphics[0]["rect"], self.graphics[0]["rotation"])

        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        h, w = roi.shape

        histogram = cv2.calcHist([roi], [0], None, [256], [0, 256])
        canvas = np.zeros((h, w), dtype=np.uint8)
        t = np.arange(0, 256, 1)
        nse = np.random.randn(len(t))
        # not cool
        for i in range(0, 255):
            nse[i] = histogram[i]

        t = w * t / 255
        nse = h * nse / nse.max()
        pts = np.vstack((t, nse)).T.astype(np.int32)
        cv2.polylines(canvas, [pts], False, (255, 0, 255), 1, cv2.LINE_4)
        canvas = cv2.rotate(canvas, cv2.ROTATE_180)
        canvas = cv2.flip(canvas, 1)
        conc_image = np.concatenate((roi, canvas), axis=1)
        self.algorithm_result.imageRoi = conc_image
        self.algorithm_result.debugImages = [conc_image]

        peaks = (-histogram).argsort(axis=0)[:6]
        peaksRange = []

        for i in range(0, 255):
            print(f'i{i}:v{histogram[i]}')

        return self.algorithm_result
