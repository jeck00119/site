from difflib import SequenceMatcher

import cv2
import numpy as np
from pytesseract import pytesseract

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_exceptions import RoiOutOfImageBoundsException, \
    InvalidImageDepthException
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.environment import TESSERACT_INSTALLATION_DIR
from src.utils import crop_roi


class OCRAlgorithm(AbstractAlgorithm):
    def __init__(self, graphics, width_resize_factor=2.0, height_resize_factor=2.0,
                 adaptive_threshold_block_size=31, adaptive_threshold_constant=10, blur_kernel_size=5,
                 opening_kernel_size=3, closing_kernel_size=7, trained_data_file="eng", expected_text: str = "",
                 chars_to_detect="", segmentation_mode="3", similarity_threshold=50.0,
                 reference_algorithm=None, golden_position=None):
        super(OCRAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                           golden_position=golden_position)
        self.expected_text = expected_text
        self.found_text = ""

        self.width_resize_factor = width_resize_factor
        self.height_resize_factor = height_resize_factor

        self.adaptive_threshold_block_size = adaptive_threshold_block_size
        self.adaptive_threshold_constant = adaptive_threshold_constant

        self.blur_kernel_size = blur_kernel_size

        self.opening_kernel_size = opening_kernel_size
        self.closing_kernel_size = closing_kernel_size

        self.trained_data_file = trained_data_file

        self.chars_to_detect = chars_to_detect
        self.segmentation_mode = segmentation_mode
        self.similarity_threshold = similarity_threshold

        # Set cross-platform Tesseract executable path
        from src.platform_utils import is_windows
        import os
        
        executable_name = "tesseract.exe" if is_windows() else "tesseract"
        pytesseract.tesseract_cmd = os.path.join(TESSERACT_INSTALLATION_DIR, executable_name)

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

        roi, coordinates = crop_roi(frame, roi_offset=self.graphics[0]["offset"],
                                    roi_bound=self.graphics[0]["bound"], roi_rect=self.graphics[0]["rect"],
                                    rotation=self.graphics[0]["rotation"])

        processed_img = frame.copy()

        # cv2.imshow("ocr", roi)
        # cv2.waitKey(0)

        if self.chars_to_detect == "":
            config_string = f"--psm {self.segmentation_mode}"
        else:
            config_string = f"-c tessedit_char_whitelist={self.chars_to_detect} --psm {self.segmentation_mode}"

        frame = self.preprocess(roi)
        found_text = pytesseract.image_to_string(frame, lang=self.trained_data_file, config=config_string)

        found_text = found_text[:-2]

        # dist = self.variation_distance(self.expectedText, found_text)
        # max_dist = max(len(self.expectedText), len(found_text))
        #
        # sim = 100 - ((dist / max_dist) * 100)

        sim = SequenceMatcher(None, self.expected_text, found_text).ratio()
        sim = sim * 100
        if sim > self.similarity_threshold:
            status = True
        else:
            status = False

        processed_img = cv2.rectangle(processed_img, (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]),
                                      (255, 0, 0), 7)

        font = cv2.FONT_HERSHEY_SIMPLEX
        size = 0.8
        text = "Found Text: " + str(found_text)

        textsize = cv2.getTextSize(text, font, size, 2)[0]
        textX = round((roi.shape[1] - textsize[0]) / 2)
        textY = 20

        cv2.putText(processed_img, text, (coordinates[0] + textX, coordinates[1] + textY), font, size, (255, 0, 0), 2)

        self.algorithm_result.debugImages = [processed_img, roi]
        self.algorithm_result.imageRoi = processed_img
        self.algorithm_result.data = {
            "foundText": found_text
        }
        self.algorithm_result.inspections_name = {f'label_{self.inspection_name}': status}
        return self.algorithm_result

    def preprocess(self, image):
        resized = cv2.resize(image, None, fx=self.width_resize_factor, fy=self.height_resize_factor,
                             interpolation=cv2.INTER_CUBIC)

        # kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        # sharp = cv2.filter2D(resized, -1, kernel)

        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        mask = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                                     self.adaptive_threshold_block_size, self.adaptive_threshold_constant)

        blur = cv2.medianBlur(mask, self.blur_kernel_size)

        inverted = cv2.bitwise_not(blur)

        kernel = np.ones((self.opening_kernel_size, self.opening_kernel_size), np.uint8)
        opened = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, kernel)

        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (self.closing_kernel_size, self.closing_kernel_size))
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)

        kernel = np.eye(self.closing_kernel_size, dtype=np.uint8)
        closed = cv2.morphologyEx(closed, cv2.MORPH_CLOSE, kernel)

        kernel = np.flip(kernel, axis=1)
        closed = cv2.morphologyEx(closed, cv2.MORPH_CLOSE, kernel)

        result = cv2.bitwise_not(closed)

        # cv2.imshow("res", algorithmResult)
        # cv2.waitKey(0)
        return result

    def correct_skew(self, img):
        # height, width = img.shape[:2]
        #
        # m = cv2.getOptimalDFTSize(height)
        # n = cv2.getOptimalDFTSize(width)
        #
        # padded = cv2.copyMakeBorder(img, 0, m - height, 0, n - width, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        #
        # planes = [np.float32(padded), np.zeros(padded.shape, np.float32)]
        #
        # complex_img = cv2.merge(planes)
        #
        # cv2.dft(complex_img, complex_img)
        #
        # cv2.split(complex_img, planes)
        #
        # cv2.magnitude(planes[0], planes[1], planes[0])
        #
        # mag_img = planes[0]
        #
        # mat_of_ones = np.ones(mag_img.shape, mag_img.dtype)
        # cv2.add(mat_of_ones, mag_img, mag_img)
        # cv2.log(mag_img, mag_img)
        #
        # mag_img_height, mag_img_width = mag_img.shape[:2]
        #
        # mag_img = mag_img[0:(mag_img_height & -2), 0:(mag_img_width & -2)]
        #
        # cx = int(mag_img_height / 2)
        # cy = int(mag_img_width / 2)
        #
        # q0 = mag_img[0:cx, 0:cy]
        # q1 = mag_img[cx:cx + cx, 0:cy]
        # q2 = mag_img[0:cx, cy:cy + cy]
        # q3 = mag_img[cx:cx + cx, cy:cy + cy]
        #
        # tmp = np.copy(q0)
        #
        # mag_img[cx:cx + cx, 0:cy] = q2
        # mag_img[0:cx, cy:cy + cy] = tmp
        #
        # cv2.normalize(mag_img, mag_img, 0, 1, cv2.NORM_MINMAX)
        #
        # mag_img = np.asarray(mag_img, dtype=np.uint8)
        #
        # mask = cv2.adaptiveThreshold(mag_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
        #                              self.adaptiveThresholdBlockSize, self.adaptiveThresholdConstant)

        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        mag_img = 20 * np.log(np.abs(fshift))
        mag_img = np.asarray(mag_img, dtype=np.uint8)

        mag_img = cv2.GaussianBlur(mag_img, (7, 7), 0.87)

        mask = cv2.threshold(mag_img, 200, 255, cv2.THRESH_BINARY)[1]

        # kernel = np.ones((13, 13), dtype=np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 13))
        mask = cv2.morphologyEx(mask, cv2.MORPH_ERODE, kernel)

        kernel = np.ones((51, 51), dtype=np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        cv2.imshow("input image", img)
        cv2.imshow("spectrum magnitude", mag_img)
        cv2.imshow("bin", mask)
        cv2.waitKey(0)

        cv2.imwrite("spectre.png", mag_img)

    @staticmethod
    def text_variations(word):
        variations_text = {"0": "O",
                           "D": "0,O",
                           "O": "0",
                           "I": "l,1"
                           }

        variations_text = {k: v.split(',') for k, v in variations_text.items()}
        word_list = [word]

        for word in word_list:
            for char in variations_text:
                for r in variations_text[char]:
                    pos = 0
                    current_word = word
                    while current_word.find(char, pos) != -1:
                        pos = current_word.find(char, pos)
                        current_word = current_word[:pos] + r + current_word[pos + 1:]
                        pos += 1
                        if current_word not in word_list:
                            word_list.append(current_word)
                        current_word = word
        return word_list

    @staticmethod
    def levenshtein_distance(a, b):
        """Return the Levenshtein edit distance between two strings *a* and *b*."""
        if a == b:
            return 0
        if len(a) < len(b):
            a, b = b, a
        if not a:
            return len(b)
        previous_row = range(len(b) + 1)
        for i, column1 in enumerate(a):
            current_row = [i + 1]
            for j, column2 in enumerate(b):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (column1 != column2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def variation_distance(self, expected_word, real_word):
        distance_min = 1000  # initialized with rude value
        variations = self.text_variations(expected_word)
        for variation in variations:
            distance = self.levenshtein_distance(variation, real_word)
            if distance < distance_min:
                distance_min = distance
        return distance_min
