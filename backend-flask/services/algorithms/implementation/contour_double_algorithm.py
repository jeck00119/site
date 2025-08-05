import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import adjust_gamma, crop_roi


class ContourDoubleAlgorithm(AbstractAlgorithm):
    def __init__(self, white_threshold, black_threshold, dilate_kernel, dilate_iterations, erode_kernel,
                 erode_iterations, blur_kernel, part_area_min, part_area_max, gamma, enable_inv_binarization,
                 enable_adaptive_threshold, adaptive_offset, enable_histogram_debug, graphics, reference_algorithm=None,
                 golden_position=None):
        super(ContourDoubleAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                     golden_position=golden_position)

        self.white_threshold = white_threshold
        self.black_threshold = black_threshold

        self.gamma = gamma

        self.erode_kernel = erode_kernel
        self.erode_iterations = erode_iterations

        self.dilate_kernel = dilate_kernel
        self.dilate_iterations = dilate_iterations

        self.blur_kernel = blur_kernel

        self.part_area_min = part_area_min
        self.part_area_max = part_area_max

        self.enable_inv_binarization = enable_inv_binarization

        self.enable_adaptive_threshold = enable_adaptive_threshold
        self.adaptive_offset = adaptive_offset
        self.enable_histogram_debug = enable_histogram_debug

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        roi, coordinates = crop_roi(frame, roi_offset=self.graphics[0]["offset"],
                                    roi_bound=self.graphics[0]["bound"], roi_rect=self.graphics[0]["rect"],
                                    rotation=self.graphics[0]["rotation"])

        roi = adjust_gamma(roi, float(self.gamma))
        color = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        histogram = 0

        if self.enable_adaptive_threshold:
            self.black_threshold, self.white_threshold, sign, histogram = self.find_adaptive_threshold(
                roi, self.adaptive_offset)

        result, contour_list, binary_roi = self.process(roi, color)

        cv2.drawContours(color, contour_list, -1, (255, 0, 255), 4)
        if self.enable_histogram_debug and self.enable_adaptive_threshold:
            h, w = binary_roi.shape

            canvas = np.zeros((h, w), dtype=np.uint8)
            t = np.arange(0, 256, 1)
            nse = np.random.randn(len(t))
            # not cool
            for i in range(0, 255):
                nse[i] = histogram[i]

            t = w * t / 255
            nse = h * nse / nse.max()
            pts = np.vstack((t, nse)).T.astype(np.int32)
            cv2.polylines(canvas, [pts], False, (255, 0, 255), 2, cv2.LINE_4)
            canvas = cv2.rotate(canvas, cv2.ROTATE_180)
            canvas = cv2.flip(canvas, 1)
            vis = np.concatenate((binary_roi, canvas), axis=1)
            binary_roi = vis

        cv2.putText(color, str(result), (100, 100), cv2.FONT_HERSHEY_DUPLEX, 3, (255, 0, 0), 3)

        processed_img = cv2.rectangle(frame.copy(), (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]),
                                     (255, 0, 0), 5)
        processed_img[coordinates[1]:coordinates[3] - 1, coordinates[0]:coordinates[2] - 1] = color

        self.algorithm_result.data = {
            "result": result
        }
        self.algorithm_result.imageRoi = cv2.cvtColor(binary_roi, cv2.COLOR_GRAY2RGB)
        self.algorithm_result.debugImages = [processed_img, cv2.cvtColor(binary_roi, cv2.COLOR_GRAY2RGB),
                                             cv2.cvtColor(color, cv2.COLOR_RGB2BGR)]
        return self.algorithm_result

    def process(self, roi, color):
        thr, binary_roi = cv2.threshold(roi, self.white_threshold, 255, cv2.THRESH_BINARY)
        binary_roi = self.pre_process(binary_roi)
        contour_list = self.find_contours(binary_roi, color)
        if len(contour_list) > 0:
            return 1, contour_list, binary_roi
        else:
            thr, binary_roi = cv2.threshold(roi, self.black_threshold, 255, cv2.THRESH_BINARY_INV)
            binary_roi = self.pre_process(binary_roi)
            contour_list = self.find_contours(binary_roi, color)
            if len(contour_list) > 0:
                return 0, contour_list, binary_roi
            else:
                return -1, [], binary_roi

    def pre_process(self, binary_roi):
        kernel_dilate = np.ones((self.dilate_kernel, self.dilate_kernel), np.uint8)
        kernel_erode = np.ones((self.erode_kernel, self.erode_kernel), np.uint8)

        if self.blur_kernel % 2 == 0:
            self.blur_kernel += 1
        binary_roi = cv2.GaussianBlur(binary_roi, (self.blur_kernel, self.blur_kernel), 0)
        binary_roi = cv2.erode(binary_roi, kernel_erode, iterations=self.erode_iterations)
        binary_roi = cv2.dilate(binary_roi, kernel_dilate, iterations=self.dilate_iterations)
        return binary_roi

    def find_contours(self, binary_roi, color):
        contours, h = cv2.findContours(binary_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        contour_list = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.part_area_min < area < self.part_area_max:
                contour_list.append(contour)
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(color, (x, y), (x + w, y + h), (0, 255, 0), 5)
        return contour_list

    def find_adaptive_threshold(self, roi, offset):
        hist_full = cv2.calcHist([roi], [0], None, [256], [0, 256])

        peaks = (-hist_full).argsort(axis=0)[:6]
        peaksRange = []

        for peak in peaks:
            peaksRange.append(sumPeak(hist_full, peak))

        index = np.argmax(peaksRange)

        if peaks[index] + offset >= 255:
            white_threshold = 240
        else:
            white_threshold = peaks[index] + offset

        black_threshold = peaks[index] - offset
        try:
            black_threshold = black_threshold[0]
        except TypeError:
            pass

        try:
            white_threshold = white_threshold[0]
        except TypeError:
            pass

        return black_threshold, white_threshold, peaks[index], hist_full


def sumPeak(histogram, peak):
    if peak - 10 < 0:
        peakLow = 0
    else:
        peakLow = peak - 10

    if peak + 10 > 255:
        peakHigh = 255
    else:
        peakHigh = peak + 10

    sumPeak = 0
    for i in range(int(peakLow), int(peakHigh)):
        sumPeak = histogram[i] + sumPeak

    return sumPeak
