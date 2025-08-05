import os

import cv2
import numpy as np
from scipy.spatial import distance as dist

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_exceptions import RoiOutOfImageBoundsException, \
    InvalidImageDepthException
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.environment import DEBUG_FOLDER_PATH
from src.utils import crop_roi, split_rectangle_in_4


class LabelDetectionAlgorithm(AbstractAlgorithm):
    def __init__(self, graphics, blur_kernel_size, bin_lower_threshold, bin_upper_threshold, canny_first_threshold,
                 canny_second_threshold, white_region_threshold, board_angle_offset, app_type,
                 reference_algorithm=None, golden_position=None):
        super().__init__(graphics, reference_algorithm=reference_algorithm, golden_position=golden_position)

        # Label parameters

        self.blur_kernel_size = blur_kernel_size
        self.bin_lower_threshold = bin_lower_threshold
        self.bin_upper_threshold = bin_upper_threshold
        self.canny_first_threshold = canny_first_threshold
        self.canny_second_threshold = canny_second_threshold
        self.white_region_threshold = white_region_threshold
        self.board_angle_offset = board_angle_offset
        self.app_type = app_type

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        height, width, channels = frame.shape
        cv2.imwrite(os.path.join(DEBUG_FOLDER_PATH, 'frame_label.png'), frame)

        for roi in self.graphics:
            x = roi["bound"][0]
            y = roi["bound"][1]
            roi_width = roi["bound"][2]
            roi_height = roi["bound"][3]

            if x < 0 or y < 0 or x + roi_width > width or y + roi_height > height:
                raise RoiOutOfImageBoundsException

        if channels != 3:
            raise InvalidImageDepthException(3, channels)

        offsets = [0.0, 90.0, 180.0, 270.0]
        label_width_cms = 5.3

        horizontal_distance = vertical_distance = None

        x = self.graphics[1]["bound"][0]
        y = self.graphics[1]["bound"][1]
        roi_width = self.graphics[1]["bound"][2]
        roi_height = self.graphics[1]["bound"][3]

        x_ref = int(x + roi_width / 2)
        y_ref = int(y + roi_height / 2)

        roi_ref, coordinates = crop_roi(frame, roi_offset=self.graphics[1]["offset"],
                                        roi_bound=self.graphics[1]["bound"],
                                        roi_rect=self.graphics[1]["rect"],
                                        rotation=self.graphics[1]["rotation"])

        roi, coordinates = crop_roi(frame, roi_offset=self.graphics[0]["offset"],
                                    roi_bound=self.graphics[0]["bound"],
                                    roi_rect=self.graphics[0]["rect"],
                                    rotation=self.graphics[0]["rotation"])

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur = cv2.blur(gray, (self.blur_kernel_size, self.blur_kernel_size))
        ret, mask = cv2.threshold(blur, self.bin_lower_threshold, self.bin_upper_threshold,
                                  cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        kernel = np.ones(shape=(11, 11), dtype=np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        edged = cv2.Canny(mask, self.canny_first_threshold, self.canny_second_threshold)

        contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        found_contours_roi = roi.copy()
        found_contours_max = roi.copy()

        ordered_contours = self.order_contours_by_size(contours)
        cnt = ordered_contours[0]

        cv2.drawContours(roi, cnt, -1, (255, 0, 0), 3)
        cv2.imwrite(os.path.join(DEBUG_FOLDER_PATH, 'img_contor.png'), roi)

        if cnt is not None and cv2.contourArea(cnt) > 28000:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            ordered_corners = self.order_points(box)
            ordered_corners = np.int0(ordered_corners)

            x_ctr_label = int(self.graphics[0]["bound"][0]) + int(rect[0][0])
            y_ctr_label = int(self.graphics[0]["bound"][1]) + int(rect[0][1])

            # cv2.circle(frame, (x_ctr_label, y_ctr_label), 20, (0, 255, 0), -1)

            horizontal_distance = abs(x_ctr_label - x_ref)
            vertical_distance = abs(y_ctr_label - y_ref)

            rotation_angle = None

            if ordered_corners[2][1] >= ordered_corners[3][1]:
                rotation_angle = rect[2]
                # rotation_angle = (90 - rect[2]) * -1
            else:
                rotation_angle = (90 - rect[2]) * -1
                # rotation_angle = abs(rect[2])

            rect_rotated = None
            rotated = None
            mask_rotated = None
            edged_rotated = None

            if rect[2] not in offsets:
                (h, w) = roi.shape[:2]
                M = cv2.getRotationMatrix2D((w / 2, h / 2), rotation_angle, 1.0)
                rotated = cv2.warpAffine(roi, M, (w, h))
                gray_rotated = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
                blur_rotated = cv2.blur(gray_rotated, (self.blur_kernel_size, self.blur_kernel_size))
                ret, mask_rotated = cv2.threshold(blur_rotated, self.bin_lower_threshold, self.bin_upper_threshold,
                                                  cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                edged_rotated = cv2.Canny(mask_rotated, self.canny_first_threshold, self.canny_second_threshold)
                contours_rotated, hierarchy = cv2.findContours(edged_rotated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                ordered_contours = self.order_contours_by_size(contours_rotated)
                cnt = ordered_contours[0]
                # cnt = self.find_contour_by_area(contours_rotated)
                rect_rotated = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                ordered_corners = self.order_points(box)
                ordered_corners = np.int0(ordered_corners)
            else:
                rect_rotated = rect
                rotated = roi
                mask_rotated = mask
                edged_rotated = edged

            height = 0
            width = 0
            if rect_rotated[2] > 45.0:
                width = rect_rotated[1][1]
                height = rect_rotated[1][0]
            else:
                width = rect_rotated[1][0]
                height = rect_rotated[1][1]

            pixel_value_cms = label_width_cms / width

            horizontal_distance = horizontal_distance * pixel_value_cms
            vertical_distance = vertical_distance * pixel_value_cms

            x_rect = int(rect[0][0] - (width / 2))
            y_rect = int(rect[0][1] - (height / 2))

            x_rect_rotated = int(rect_rotated[0][0] - (width / 2))
            y_rect_rotated = int(rect_rotated[0][1] - (height / 2))

            if x_rect_rotated < 0:
                x_rect_rotated = 0

            if y_rect_rotated < 0:
                y_rect_rotated = 0

            hist_size = 256

            hist_range = (0, 256)

            accumulate = False

            cv2.imwrite(os.path.join(DEBUG_FOLDER_PATH, 'label_after_rot.png'), rotated)

            top_left, top_right, bottom_left, bottom_right = split_rectangle_in_4(rotated,
                                                                                  (x_rect_rotated, y_rect_rotated),
                                                                                  width, height)

            label = rotated[y_rect_rotated:y_rect_rotated + int(height), x_rect_rotated:x_rect_rotated + int(width)]

            cv2.imwrite(os.path.join(DEBUG_FOLDER_PATH, 'detected_label.png'), label)

            # bgr_planes_top_left = cv2.split(top_left)
            # bgr_planes_top_right = cv2.split(top_right)
            # bgr_planes_bottom_left = cv2.split(bottom_left)
            # bgr_planes_bottom_right = cv2.split(bottom_right)

            channel_ids = (0, 1, 2)

            red_channel = []
            green_channel = []
            blue_channel = []

            for channel_id in channel_ids:
                histogram, bin_edges = np.histogram(
                    top_left[:, :, channel_id], bins=256, range=(0, 256)
                )

                if channel_id == 0:
                    blue_channel.append(histogram[50:].argmax())
                elif channel_id == 1:
                    green_channel.append(histogram[50:].argmax())
                else:
                    red_channel.append(histogram[50:].argmax())

                histogram, bin_edges = np.histogram(
                    top_right[:, :, channel_id], bins=256, range=(0, 256)
                )

                if channel_id == 0:
                    blue_channel.append(histogram[50:].argmax())
                elif channel_id == 1:
                    green_channel.append(histogram[50:].argmax())
                else:
                    red_channel.append(histogram[50:].argmax())

                histogram, bin_edges = np.histogram(
                    bottom_left[:, :, channel_id], bins=256, range=(0, 256)
                )

                if channel_id == 0:
                    blue_channel.append(histogram[50:].argmax())
                elif channel_id == 1:
                    green_channel.append(histogram[50:].argmax())
                else:
                    red_channel.append(histogram[50:].argmax())

                histogram, bin_edges = np.histogram(
                    bottom_right[:, :, channel_id], bins=256, range=(0, 256)
                )

                if channel_id == 0:
                    blue_channel.append(histogram[50:].argmax())
                elif channel_id == 1:
                    green_channel.append(histogram[50:].argmax())
                else:
                    red_channel.append(histogram[50:].argmax())

            # top_left_hist_b = cv2.calcHist(bgr_planes_top_left, [2], None,
            #                                [hist_size], hist_range, accumulate=accumulate)
            #
            # top_right_hist_b = cv2.calcHist(bgr_planes_top_right,
            #                                 [2], None, [hist_size], hist_range, accumulate=accumulate)
            #
            # bottom_left_hist_b = cv2.calcHist(bgr_planes_bottom_left,
            #                                   [2], None, [hist_size], hist_range, accumulate=accumulate)
            #
            # bottom_right_hist_b = cv2.calcHist(bgr_planes_bottom_right,
            #                                    [2], None, [hist_size], hist_range, accumulate=accumulate)

            # top_left_maj_b = top_left_hist_b.argmax(axis=0)
            #
            # top_right_maj_b = top_right_hist_b.argmax(axis=0)
            #
            # bottom_left_maj_b = bottom_left_hist_b.argmax(axis=0)
            #
            # bottom_right_maj_b = bottom_right_hist_b.argmax(axis=0)

            top_left_std = np.std(np.array([blue_channel[0], green_channel[0], red_channel[0]]))

            top_right_std = np.std(np.array([blue_channel[1], green_channel[1], red_channel[1]]))

            bottom_left_std = np.std(np.array([blue_channel[2], green_channel[2], red_channel[2]]))

            bottom_right_std = np.std(np.array([blue_channel[3], green_channel[3], red_channel[3]]))

            peaks = [top_left_std, top_right_std, bottom_left_std, bottom_right_std]
            peaks.sort(reverse=True)

            if 1 in peaks or peaks[1] - peaks[2] < 3:
                print("Histogram result doesn't has correct values")
            else:
                self.white_region_threshold = int((peaks[1] + peaks[2]) / 2)

            angle = None

            if (top_left_std > self.white_region_threshold) and (top_right_std > self.white_region_threshold) and \
                    (bottom_left_std < self.white_region_threshold) and (
                    bottom_right_std < self.white_region_threshold):
                if rect[2] == 90.0:
                    angle = 0.0
                else:
                    if rotation_angle < 0:
                        angle = 0.0 + abs(rotation_angle)
                    else:
                        angle = 0.0 - rotation_angle
            elif (top_left_std > self.white_region_threshold) and (top_right_std < self.white_region_threshold) and \
                    (bottom_left_std > self.white_region_threshold) and (
                    bottom_right_std < self.white_region_threshold):
                if rect[2] == 90.0:
                    angle = 90.0
                else:
                    if rotation_angle < 0:
                        angle = 90.0 + abs(rotation_angle)
                    else:
                        angle = 90.0 - rotation_angle
                    initial_height, initial_width = label.shape[:2]
                    label = cv2.copyMakeBorder(label, 0, 0, int((initial_height - initial_width) / 2),
                                               int((initial_height - initial_width) / 2), cv2.BORDER_REPLICATE)
                    (h, w) = label.shape[:2]
                    M = cv2.getRotationMatrix2D((w / 2, h / 2), -270.0, 1.0)
                    label = cv2.warpAffine(label, M, (h, w))
                    label = label[int((initial_height - initial_width) / 2):int(
                        (initial_height - initial_width) / 2) + initial_width, :]
            elif (top_left_std < self.white_region_threshold) and (top_right_std < self.white_region_threshold) and \
                    (bottom_left_std > self.white_region_threshold) and (
                    bottom_right_std > self.white_region_threshold):
                if rect[2] == 90.0:
                    angle = 180.0
                else:
                    if rotation_angle < 0:
                        angle = 180.0 + abs(rotation_angle)
                    else:
                        angle = 180.0 - rotation_angle
                    (h, w) = label.shape[:2]
                    M = cv2.getRotationMatrix2D((w / 2, h / 2), 180.0, 1.0)
                    label = cv2.warpAffine(label, M, (w, h))
            elif (top_left_std < self.white_region_threshold) and (top_right_std > self.white_region_threshold) and \
                    (bottom_left_std < self.white_region_threshold) and (
                    bottom_right_std > self.white_region_threshold):
                if rect[2] == 90.0:
                    angle = 270.0
                else:
                    if rotation_angle < 0:
                        angle = 270.0 + abs(rotation_angle)
                    else:
                        angle = 270.0 - rotation_angle
                    initial_height, initial_width = label.shape[:2]
                    label = cv2.copyMakeBorder(label, 0, 0, int((initial_height - initial_width) / 2),
                                               int((initial_height - initial_width) / 2), cv2.BORDER_REPLICATE)
                    (h, w) = label.shape[:2]
                    M = cv2.getRotationMatrix2D((w / 2, h / 2), -90.0, 1.0)
                    label = cv2.warpAffine(label, M, (h, w))
                    label = label[int((initial_height - initial_width) / 2):int(
                        (initial_height - initial_width) / 2) + initial_width, :]
        else:
            angle = 9999
            rect = None
            horizontal_distance = -1
            vertical_distance = -1
            edged_rotated = None
            rotated = None
            label = None

        passed_rotation = False
        passed_horizontal = False
        passed_vertical = False

        if angle is not None:
            if self.board_angle_offset - 2 < angle < self.board_angle_offset + 2:
                passed_rotation = True
            else:
                passed_rotation = False

            if horizontal_distance < 1.0:
                passed_horizontal = True
            else:
                passed_horizontal = False

            if vertical_distance < 1.0:
                passed_vertical = True
            else:
                passed_vertical = False

        passed = passed_rotation and passed_vertical and passed_horizontal

        self.algorithm_result.data = {
            "rotationAngle": angle,
            "labelPosition": rect,
            "verticalSideDistance": vertical_distance,
            "horizontalSideDistance": horizontal_distance,
            "pass": passed
        }

        self.algorithm_result.inspections_name = {
            f'{self.inspection_name}_displacement_x': horizontal_distance,
            f'{self.inspection_name}_displacement_y': vertical_distance,
            f'{self.inspection_name}_rotation': angle,
        }
        try:
            processed_img = cv2.rectangle(frame, (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]),
                                          (255, 0, 0), 5)
            processed_img[coordinates[1]:coordinates[3] - 1, coordinates[0]:coordinates[2] - 1] = rotated
        except:
            processed_img = frame

        font = cv2.FONT_HERSHEY_SIMPLEX
        size = 2

        text = ("rotationAngle: " + str(angle) + "{nl}" +
                "labelPosition: " + str(rect) + "{nl}" +
                "verticalSideDistance: " + str(vertical_distance) + "{nl}" +
                "horizontalSideDistance: " + str(horizontal_distance) + "{nl}" +
                "pass: " + str(passed)).format(nl="\n")

        text_x = 50
        text_y = 50

        cv2.putText(processed_img, text, (text_x, text_y), font, size, (255, 0, 0), 2)

        self.algorithm_result.imageRoi = roi
        self.algorithm_result.debugImages = [processed_img, rotated]  # [roi, mask, edged_rotated, rotated, label]
        self.algorithm_result.image = frame
        return self.algorithm_result

    @staticmethod
    def order_contours_by_size(contours: list):
        areas = []
        contours_ordered = []
        for contour in contours:
            area = cv2.arcLength(contour, True)
            areas.append(area)

        for i in range(len(areas)):
            max_value = max(areas)
            pos = areas.index(max_value)
            contours_ordered.append(contours[pos])
            areas[pos] = -1.0

        return contours_ordered

    @staticmethod
    def order_points(pts):
        # sort the points based on their x-coordinates
        x_sorted = pts[np.argsort(pts[:, 0]), :]
        # grab the left-most and right-most points from the sorted
        # x-coordinate points
        left_most = x_sorted[:2, :]
        right_most = x_sorted[2:, :]
        # now, sort the left-most coordinates according to their
        # y-coordinates so we can grab the top-left and bottom-left
        # points, respectively
        left_most = left_most[np.argsort(left_most[:, 1]), :]
        (tl, bl) = left_most
        # now that we have the top-left coordinate, use it as an
        # anchor to calculate the Euclidean distance between the
        # top-left and right-most points; by the Pythagorean
        # theorem, the point with the largest distance will be
        # our bottom-right point
        d = dist.cdist(tl[np.newaxis], right_most, "euclidean")[0]
        (br, tr) = right_most[np.argsort(d)[::-1], :]
        # return the coordinates in top-left, top-right,
        # bottom-right, and bottom-left order
        return np.array([tl, tr, br, bl], dtype="float32")
