import cv2
import imutils
import numpy as np
from scipy.spatial import distance as dist

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class CableCoverDetectionAlgorithm(AbstractAlgorithm):
    def __init__(self, median_blur, bin_thresh, kernel_opening, kernel_closing, iteration_opening,
                 iteration_closing, no_cover_area_thresh, black_silicone_cover_ext_x_min_dist,
                 blue_cover_ext_x_min_dist, expected_result, graphics, reference_algorithm=None, golden_position=None):
        super(CableCoverDetectionAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                           golden_position=golden_position)

        self.median_blur = median_blur
        self.bin_thresh = bin_thresh
        self.kernel_opening = kernel_opening
        self.kernel_closing = kernel_closing
        self.iteration_opening = iteration_opening
        self.iteration_closing = iteration_closing
        self.no_cover_area_thresh = no_cover_area_thresh
        self.black_silicone_cover_ext_x_min_dist = black_silicone_cover_ext_x_min_dist
        self.blue_cover_ext_x_min_dist = blue_cover_ext_x_min_dist
        self.expected_result = expected_result

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        processed_img = frame.copy()

        frame, coordinates = crop_roi(frame, self.graphics[0]["offset"], self.graphics[0]["bound"],
                                      self.graphics[0]["rect"], self.graphics[0]["rotation"])

        frame_color = frame.copy()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frame = cv2.medianBlur(frame, self.median_blur)

        if self.bin_thresh == 0:
            ret, frame = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            ret, frame = cv2.threshold(frame, self.bin_thresh, 255, cv2.THRESH_BINARY)

        kernel_opening = np.ones((self.kernel_opening, self.kernel_opening), np.uint8)
        frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel_opening,
                                 iterations=self.iteration_opening)
        kernel_closing = np.ones((self.kernel_closing, self.kernel_closing), np.uint8)
        frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel_closing,
                                 iterations=self.iteration_closing)
        frame = cv2.bitwise_not(frame)

        frame_bin_hist, bins = np.histogram(frame.ravel(), 256, [0, 256])

        frame_gray = cv2.cvtColor(frame_color, cv2.COLOR_BGR2GRAY)
        ret, frame_low_thresh_binary = cv2.threshold(frame_gray, 60, 255, cv2.THRESH_BINARY)
        frame_low_thresh_binary = cv2.bitwise_not(frame_low_thresh_binary)
        frame_low_thresh_binary_hist, bins_binary = np.histogram(frame_low_thresh_binary.ravel(), 256, [0, 256])

        min_white_pixels_thresh_perc_dim = 0.025 * (frame_low_thresh_binary.shape[0] * frame_low_thresh_binary.shape[1])

        if frame_low_thresh_binary_hist[255] < min_white_pixels_thresh_perc_dim:
            frame = frame_low_thresh_binary.copy()
            frame_bin_hist, bins = np.histogram(frame.ravel(), 256, [0, 256])

        if frame_low_thresh_binary_hist[255] < min_white_pixels_thresh_perc_dim or frame_bin_hist[
            255] < self.no_cover_area_thresh:
            result = [0, "No Cover", True]

            frame_border = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            cv2.putText(frame_border, 'white pixels: ' + str(frame_bin_hist[255]), (5, 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        else:
            frame_border = cv2.copyMakeBorder(
                frame, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            frame = cv2.copyMakeBorder(
                frame, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[0, 0, 0])

            cnts = cv2.findContours(frame_border, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            c = max(cnts, key=cv2.contourArea)

            ext_left = tuple(c[c[:, :, 0].argmin()][0])
            ext_right = tuple(c[c[:, :, 0].argmax()][0])

            frame_border = cv2.cvtColor(frame_border, cv2.COLOR_GRAY2BGR)

            cv2.drawContours(frame_border, [c], -1, (0, 255, 255), 2)

            cv2.circle(frame_border, ext_left, 8, (0, 255, 0), -1)
            cv2.circle(frame_border, ext_right, 8, (0, 255, 0), -1)

            cover_ext_left_ext_right_dist = round(dist.euclidean(ext_left, ext_right))

            cv2.putText(frame_border, 'cover extL & extR dist: ' + str(cover_ext_left_ext_right_dist), (5, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 1, cv2.LINE_AA)
            cv2.putText(frame_border, 'white pixels: ' + str(frame_bin_hist[255]), (5, 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            if cover_ext_left_ext_right_dist > self.black_silicone_cover_ext_x_min_dist:
                result = [3, "Black-Silicone Cover", True]
            elif cover_ext_left_ext_right_dist > self.blue_cover_ext_x_min_dist:
                result = [1, "Blue Cover", True]
            else:
                result = [2, "Black-Plastic Cover", True]

        if self.expected_result != result[1]:
            result[2] = False

        if self.expected_result == 0:
            result[0] = "No Cover"
        if self.expected_result == 1:
            result[0] = "Blue Cover"
        if self.expected_result == 2:
            result[0] = "Black-Plastic Cover"
        if self.expected_result == 3:
            result[0] = "Black-Silicone Cover"

        font = cv2.FONT_HERSHEY_SIMPLEX
        size = 0.5
        text = "Detected Cover : " + str(result[1])

        text_size = cv2.getTextSize(text, font, size, 2)[0]
        text_x = round((frame.shape[1] - text_size[0]) / 2)
        text_y = 20

        processed_img = cv2.rectangle(processed_img, (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]),
                                      (255, 0, 0), 7)
        cv2.putText(processed_img, text, (coordinates[0] + text_x, coordinates[1] - text_y), font, size, (255, 0, 0), 2)

        self.algorithm_result.data = {
            "result": result[0]
        }
        self.algorithm_result.imageRoi = frame_border
        self.algorithm_result.debugImages = [processed_img, frame]

        return self.algorithm_result
