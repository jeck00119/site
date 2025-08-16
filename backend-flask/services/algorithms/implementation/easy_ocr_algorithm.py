import copy
import time

import cv2
import easyocr
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class EasyOCRAlgorithm(AbstractAlgorithm):
    def __init__(self, graphics, threshold, invert_thresholding, blur_size, reference_algorithm=None,
                 golden_position=None):
        super(EasyOCRAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                               golden_position=golden_position)
        self.reader = easyocr.Reader(['en'])
        self.threshold = threshold
        self.invert_thresholding = invert_thresholding
        self.blur_size = blur_size

    def execute(self, frame: np.ndarray):
        frame_copy = frame.copy()

        self.algorithm_result = AlgorithmResult()

        graphics_copy = copy.deepcopy(self.graphics)

        displacement = [0, 0]

        if self.reference_algorithm is not None:
            algorithm_result = self.reference_algorithm.execute(frame_copy)
            if algorithm_result.data.x is not None:
                displacement = [algorithm_result.data.x, algorithm_result.data.y]
                for roi in graphics_copy:
                    roi["bound"][0] += algorithm_result.data.x
                    roi["bound"][1] += algorithm_result.data.y

        roi, coordinates = crop_roi(frame_copy, roi_offset=graphics_copy[0]["offset"],
                                    roi_bound=graphics_copy[0]["bound"], roi_rect=graphics_copy[0]["rect"],
                                    rotation=graphics_copy[0]["rotation"])

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        blur = cv2.medianBlur(gray, self.blur_size)

        if self.invert_thresholding:
            _, threshold = cv2.threshold(blur, self.threshold, 255, cv2.THRESH_BINARY)
        else:
            _, threshold = cv2.threshold(blur, self.threshold, 255, cv2.THRESH_BINARY_INV)

        result = self.reader.readtext(roi)

        for (bbox, text, prob) in result:
            (top_left, top_right, bottom_right, bottom_left) = bbox

            # roi = cv2.rectangle(roi, top_left, bottom_right, (0, 255, 0), 2)

            print(top_left, top_right, bottom_right, bottom_left)

            text_box_image = threshold[int(top_left[1]):int(bottom_left[1]), int(top_left[0]):int(top_right[0])]
            roi_box_image = roi[int(top_left[1]):int(bottom_left[1]), int(top_left[0]):int(top_right[0])]

            timestamp = ''.join(str(time.time()).split('.'))
            filename = timestamp + '.png'
            roi_filename = timestamp + '_roi.png'
            cv2.imwrite(f'ocr_images/{filename}', text_box_image)
            cv2.imwrite(f'ocr_images/{roi_filename}', roi_box_image)

            print(f'Text: {text}, Probability: {prob}')

        self.algorithm_result.image = frame
        self.algorithm_result.imageRoi = roi
        self.algorithm_result.debugImages = [roi, threshold]
        return self.algorithm_result
