import cv2
import numpy as np
from pyzbar.pyzbar import decode

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class BarcodeScanAlgorithm(AbstractAlgorithm):
    def __init__(self, graphics, threshold_enabled: bool = False, block_size: int = 11, c: int = 2,
                 reference_algorithm=None, golden_position=None):
        super(BarcodeScanAlgorithm, self).__init__(graphics=graphics, reference_algorithm=reference_algorithm,
                                                   golden_position=golden_position)
        self.threshold_enabled = threshold_enabled
        self.block_size = block_size
        self.c = c

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        roi, coordinates = crop_roi(frame, self.graphics[0]["offset"], self.graphics[0]["bound"],
                                    self.graphics[0]["rect"], self.graphics[0]["rotation"])

        if self.threshold_enabled:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            process_roi = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                                                self.block_size, self.c)
        else:
            process_roi = roi.copy()

        barcodes = decode(process_roi)
        code = None
        height = roi.shape[0]
        width = roi.shape[1]
        if not barcodes:
            cv2.putText(roi, "Barcode", (50, int(height / 2)), cv2.FONT_HERSHEY_SIMPLEX,
                        width / height + height / width, (0, 0, 255), 2,
                        cv2.LINE_AA)
            cv2.putText(roi, "not found", (50, int(height / 2 + 100)), cv2.FONT_HERSHEY_SIMPLEX,
                        width / height + height / width,
                        (0, 0, 255), 2, cv2.LINE_AA)
        else:
            for barcode in barcodes:
                code = barcode.data.decode("utf-8")
                (x, y, w, h) = barcode.rect
                cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 10)
                cv2.putText(roi, code, (x, y + h + 50), cv2.FONT_HERSHEY_TRIPLEX,
                            0.45 * (width / height + height / width), (0, 255, 0),
                            1, cv2.LINE_AA)

        processed_img = cv2.rectangle(frame.copy(), (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]),
                                      (255, 0, 0), 7)
        processed_img[coordinates[1]:coordinates[3] - 1, coordinates[0]:coordinates[2] - 1] = roi

        self.algorithm_result.data = {
            "code": code
        }
        self.algorithm_result.image = frame
        self.algorithm_result.imageRoi = processed_img
        self.algorithm_result.debugImages = [processed_img, frame]
        return self.algorithm_result
