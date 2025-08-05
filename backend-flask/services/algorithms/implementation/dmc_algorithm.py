import cv2
import numpy as np
from pylibdmtx import pylibdmtx

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_exceptions import RoiOutOfImageBoundsException, \
    InvalidImageDepthException
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult


class DmcDetectionAlgorithm(AbstractAlgorithm):
    HELP = "This algorithm uses a photo and decodes a dmc"

    def __init__(self, threshold, gap_size, deviation, char_number, shrink, shape, max_count,
                 min_edge, max_edge, corrections, timeout, graphics, reference_algorithm=None, golden_position=None):
        super().__init__(graphics, reference_algorithm=reference_algorithm, golden_position=golden_position)
        self.threshold = threshold
        self.gap_size = gap_size
        self.deviation = deviation
        self.char_number = char_number
        self.shrink = shrink
        self.shape = shape
        self.max_count = max_count
        self.min_edge = min_edge
        self.max_edge = max_edge
        self.corrections = corrections
        self.timeout = timeout

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        roi_text = np.zeros([150, 300, 3], dtype=np.uint8)
        roi_text.fill(255)
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

        # roi, coordinates = crop_roi(frame, roi_offset=self.graphics[0]["offset"],
        #                             roi_bound=self.graphics[0]["bound"],
        #                             roi_rect=self.graphics[0]["rect"], rotation=self.graphics[0]["rotation"])
        roi = frame

        text = None
        shrink = self.shrink if self.shrink > 0 else None
        timeout = self.timeout if self.timeout > 0 else None
        threshold = self.threshold if self.threshold > 0 else None
        gap_size = self.gap_size if self.gap_size > 0 else None
        shape = self.shape if self.shape > 0 else None
        deviation = self.deviation if self.deviation > 0 else None
        corrections = self.corrections if self.corrections > 0 else None
        min_edge = self.min_edge if self.min_edge > 0 else None
        max_edge = self.max_edge if self.max_edge > 0 else None
        max_count = self.max_count if self.max_count > 0 else None

        barcode = pylibdmtx.decode(roi, timeout=3000, shrink=shrink)
        # barcode = zxingcpp.read_barcodes(roi)

        barcode_data = ''
        if barcode:
            barcode_data = barcode[0].data.decode("utf-8")

            cv2.rectangle(roi, (barcode[0].rect.left, barcode[0].rect.top),
                          (barcode[0].rect.left + barcode[0].rect.width, barcode[0].rect.top + barcode[0].rect.height), (0, 255, 0), 4)
            if self.char_number != 0:
                if len(barcode_data) != self.char_number:
                    text = "Error DMC not at char len"
            if barcode_data:
                try:
                    int(barcode_data)
                    cv2.putText(roi, f'{barcode_data}', (barcode[0].rect.left + barcode[0].rect.width, barcode[0].rect.top + 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                (255, 0, 0), 2, cv2.LINE_AA)

                except ValueError:
                    text = ''
        else:
            text = 'None'
        cv2.putText(roi_text, text, (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(roi_text, "dmc:" + str(barcode_data), (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)

        self.algorithm_result.imageRoi = roi
        self.algorithm_result.debugImages = [roi]
        if text != NotImplementedError:
            self.algorithm_result.data = {
                "barcode": barcode_data
            }
        return self.algorithm_result
