import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_exceptions import RoiOutOfImageBoundsException, \
    InvalidImageDepthException
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class ForegroundSubtractionAlgorithm(AbstractAlgorithm):
    modes = {
        "RECTANGLE": cv2.GC_INIT_WITH_RECT,
        "MASK": cv2.GC_INIT_WITH_MASK,
        "BOTH": cv2.GC_INIT_WITH_RECT | cv2.GC_INIT_WITH_MASK
    }

    def __init__(self, graphics, iterations, current_mode, mask_path, reference_algorithm=None, golden_position=None):
        super(ForegroundSubtractionAlgorithm, self).__init__(graphics,
                                                             reference_algorithm=reference_algorithm,
                                                             golden_position=golden_position)
        self.iterations = iterations
        self.current_mode = current_mode
        self.mask_path = mask_path

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

        roi, _ = crop_roi(frame, roi_offset=self.graphics[0]["offset"],
                          roi_bound=self.graphics[0]["bound"],
                          roi_rect=self.graphics[0]["rect"], rotation=self.graphics[0]["rotation"])

        if self.modes[self.current_mode] == cv2.GC_INIT_WITH_MASK:
            mask = np.zeros(roi.shape[:2], dtype=np.uint8)
            if self.mask_path != "":
                input_mask = cv2.imread(self.mask_path, 0)
                input_mask_roi, _ = crop_roi(input_mask,
                                             roi_offset=self.graphics[0]["offset"],
                                             roi_bound=self.graphics[0]["bound"],
                                             roi_rect=self.graphics[0]["rect"],
                                             rotation=self.graphics[0]["rotation"])
                mask[input_mask_roi == 0] = 0
                mask[input_mask_roi == 255] = 1
            rect = None
        elif self.modes[self.current_mode] == cv2.GC_INIT_WITH_RECT:
            mask = np.zeros(roi.shape[:2], dtype=np.uint8)
            rect = (int(self.graphics[1]["rect"][0]) - int(self.graphics[0]["rect"][0]),
                    int(self.graphics[1]["rect"][1]) - int(self.graphics[0]["rect"][1]),
                    int(self.graphics[1]["rect"][2]),
                    int(self.graphics[1]["rect"][3]))
        else:
            mask = np.zeros(roi.shape[:2], dtype=np.uint8)
            if self.mask_path != "":
                input_mask = cv2.imread(self.mask_path, 0)
                input_mask_roi, _ = crop_roi(input_mask,
                                             roi_offset=self.graphics[0]["offset"],
                                             roi_bound=self.graphics[0]["bound"],
                                             roi_rect=self.graphics[0]["rect"],
                                             rotation=self.graphics[0]["rotation"])
                mask[input_mask_roi == 0] = 0
                mask[input_mask_roi == 255] = 1

            rect = (int(self.graphics[1]["rect"][0]) - int(self.graphics[0]["rect"][0]),
                    int(self.graphics[1]["rect"][1]) - int(self.graphics[0]["rect"][1]),
                    int(self.graphics[1]["rect"][2]),
                    int(self.graphics[1]["rect"][3]))

        initial_mask = mask * 255

        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        cv2.grabCut(roi, mask, rect, bgd_model, fgd_model, self.iterations, self.current_mode)

        res_mask = np.where((mask == 2) | (mask == 0), 0, 1).astype(dtype=np.uint8)

        res = roi * res_mask[:, :, np.newaxis]

        res_mask = res_mask * 255

        self.algorithm_result.debugImages = [roi, initial_mask, res_mask, res]
        self.algorithm_result.imageRoi = roi

        return self.algorithm_result
