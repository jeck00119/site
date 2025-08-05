import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class ScratchDetectionTemplateAlgorithm(AbstractAlgorithm):
    def __init__(self, mode, width_downsize_factor, height_downsize_factor, alpha, beta, image_denoising_strength,
                 template_window_size, search_window_size, first_blur_kernel, sobel_kernel, second_blur_kernel,
                 threshold, closing_kernel, opening_kernel, min_obj_area, hough_threshold, min_line_length, max_gap,
                 dilation_kernel, adaptive_threshold_block_size, adaptive_threshold_constant, gaussian_kernel,
                 gaussian_sigma, template_save_location, template_load_location, graphics, reference_algorithm=None,
                 golden_position=None):
        super(ScratchDetectionTemplateAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                                golden_position=golden_position)
        self.mode = mode
        self.width_downsize_factor = width_downsize_factor
        self.height_downsize_factor = height_downsize_factor
        self.alpha = alpha
        self.beta = beta
        self.image_denoising_strength = image_denoising_strength
        self.template_window_size = template_window_size
        self.search_window_size = search_window_size
        self.first_blur_kernel = first_blur_kernel
        self.sobel_kernel = sobel_kernel
        self.second_blur_kernel = second_blur_kernel
        self.threshold = threshold
        self.closing_kernel = closing_kernel
        self.opening_kernel = opening_kernel
        self.min_obj_area = min_obj_area
        self.hough_threshold = hough_threshold
        self.min_line_length = min_line_length
        self.max_gap = max_gap
        self.dilation_kernel = dilation_kernel
        self.adaptive_threshold_block_size = adaptive_threshold_block_size
        self.adaptive_threshold_constant = adaptive_threshold_constant
        self.gaussian_kernel = gaussian_kernel
        self.gaussian_sigma = gaussian_sigma
        self.template_save_location = template_save_location
        self.template_load_location = template_load_location

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        roi, coordinates = crop_roi(frame, roi_offset=self.graphics[0]["offset"],
                                    roi_bound=self.graphics[0]["bound"], roi_rect=self.graphics[0]["rect"],
                                    rotation=self.graphics[0]["rotation"])

        if self.mode == "Detection":
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            resized = cv2.resize(gray, None, fx=(1.0 / self.width_downsize_factor),
                                 fy=(1.0 / self.height_downsize_factor),
                                 interpolation=cv2.INTER_CUBIC)

            if self.template_load_location != "":
                ref = cv2.imread(self.template_load_location, 0)
                ref = cv2.threshold(ref, 127, 255, cv2.THRESH_BINARY)[1]
                ref_resized = cv2.resize(ref, None, fx=(1.0 / self.width_downsize_factor),
                                         fy=(1.0 / self.height_downsize_factor), interpolation=cv2.INTER_CUBIC)
            else:
                ref_resized = np.zeros(shape=(resized.shape[0], resized.shape[1]), dtype=np.uint8)

            # clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(2, 2))
            # image_clahe = clahe.apply(gray)

            image_clahe = cv2.GaussianBlur(resized, (self.gaussian_kernel, self.gaussian_kernel), self.gaussian_sigma)

            contrast = self.alpha * image_clahe + self.beta
            contrast = np.clip(contrast, 0, 255).astype(np.uint8)

            denoised = cv2.fastNlMeansDenoising(contrast, None, self.image_denoising_strength,
                                                self.template_window_size, self.search_window_size)

            median = cv2.medianBlur(denoised, self.first_blur_kernel)

            sobelx = cv2.Sobel(median, cv2.CV_64F, 1, 0, ksize=self.sobel_kernel, scale=1, delta=0,
                               borderType=cv2.BORDER_DEFAULT)  # x
            sobely = cv2.Sobel(median, cv2.CV_64F, 0, 1, ksize=self.sobel_kernel, scale=1, delta=0,
                               borderType=cv2.BORDER_DEFAULT)  # y

            abs_grad_x = cv2.convertScaleAbs(sobelx)
            abs_grad_y = cv2.convertScaleAbs(sobely)

            gradient_magnitude = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)

            gradient_magnitude = cv2.medianBlur(gradient_magnitude, self.second_blur_kernel)

            img = roi.copy()
            proc_frame = frame

            ret, binary = cv2.threshold(gradient_magnitude, self.threshold, 255, cv2.THRESH_BINARY)

            and_op = cv2.bitwise_and(binary, ref_resized)

            kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,
                                               (self.closing_kernel, self.closing_kernel))

            closing = cv2.morphologyEx(and_op, cv2.MORPH_CLOSE, kernel)

            closing = np.uint8(closing)
            remove = np.zeros(closing.shape, dtype=np.uint8)

            cnts = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            for c in cnts:
                area = cv2.contourArea(c)
                if area > self.min_obj_area:
                    cv2.drawContours(remove, [c], -1, 255, -1, 1)

            remove = cv2.bitwise_and(remove, closing)

            lines = cv2.HoughLinesP(and_op, 1, np.pi / 180, self.hough_threshold, None,
                                    self.min_line_length, self.max_gap)

            scratches_found = False

            contours = cv2.findContours(remove, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

            if len(contours) != 0:
                for cnt in contours:
                    cv2.drawContours(roi, cnt, -1, (0, 0, 255), 5)

                scratches_found = True

            # if lines is not None:
            #     for line in lines:
            #         cv2.line(img, (line[0][0], line[0][1]), (line[0][2], line[0][3]), (0, 255, 0), 1)
            #         cv2.line(proc_frame, (line[0][0] + int(self.graphics[0]["roiBound"][0]),
            #                               line[0][1] + int(self.graphics[0]["roiBound"][1])),
            #                  (line[0][2] + int(self.graphics[0]["roiBound"][0]),
            #                   line[0][3] + int(self.graphics[0]["roiBound"][1])), (0, 255, 0), 1)
            #
            #     scratches_found = True

            inter = cv2.hconcat([image_clahe, contrast, denoised, gradient_magnitude, binary, and_op, remove])

            processed_img = cv2.rectangle(frame, (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]),
                                          (255, 0, 0), 7)
            processed_img[coordinates[1]:coordinates[3] - 1, coordinates[0]:coordinates[2] - 1] = roi

            self.algorithm_result.data = {
                "cracked": scratches_found
            }
            self.algorithm_result.imageRoi = inter
            self.algorithm_result.debugImages = [processed_img, inter, roi]
        else:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            denoised = cv2.fastNlMeansDenoising(gray, None, self.image_denoising_strength,
                                                self.template_window_size, self.search_window_size)
            blur = cv2.GaussianBlur(denoised, (self.gaussian_kernel, self.gaussian_kernel), self.gaussian_sigma)
            binary = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                                           self.adaptive_threshold_block_size, self.adaptive_threshold_constant)
            # ret, binary = cv2.threshold(gray, self.threshold, 255, cv2.THRESH_BINARY)

            rev = cv2.bitwise_not(binary)

            opening = cv2.morphologyEx(rev, cv2.MORPH_OPEN,
                                       kernel=np.ones(shape=(self.opening_kernel, self.opening_kernel), dtype=np.uint8))
            # rev = cv2.bitwise_not(dilated)

            closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE,
                                       kernel=np.ones(shape=(self.closing_kernel, self.closing_kernel), dtype=np.uint8))

            remove = np.zeros(closing.shape, dtype=np.uint8)

            cnts = cv2.findContours(closing, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            for c in cnts:
                area = cv2.contourArea(c)
                if area > self.min_obj_area:
                    cv2.drawContours(remove, [c], -1, 255, -1, 1)

            remove = cv2.bitwise_and(remove, closing)

            dilated = cv2.morphologyEx(remove, cv2.MORPH_DILATE,
                                       kernel=np.ones(shape=(self.dilation_kernel, self.dilation_kernel), dtype=np.uint8))

            inv = cv2.bitwise_not(dilated)

            if self.template_save_location != "":
                cv2.imwrite(self.template_save_location, inv)

            self.algorithm_result.imageRoi = inv
            self.algorithm_result.debugImages = [inv]

        return self.algorithm_result
