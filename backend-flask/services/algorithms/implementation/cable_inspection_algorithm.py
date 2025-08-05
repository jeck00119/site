import math
import time

import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_exceptions import RoiOutOfImageBoundsException, \
    InvalidImageDepthException
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class CableInspectionAlgorithm(AbstractAlgorithm):
    def __init__(self, blur_kernel_size, bin_lower_threshold, bin_upper_threshold, canny_first_threshold,
                 canny_second_threshold, flatten_contour_step, threshold_angle, contour_variation_epsilon,
                 reference_distance, absolute_distance, graphics, reference_algorithm=None, golden_position=None):
        super(CableInspectionAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                       golden_position=golden_position)
        self.blur_kernel_size = blur_kernel_size
        self.bin_lower_threshold = bin_lower_threshold
        self.bin_upper_threshold = bin_upper_threshold
        self.canny_first_threshold = canny_first_threshold
        self.canny_second_threshold = canny_second_threshold
        self.flatten_contour_step = flatten_contour_step
        self.threshold_angle = threshold_angle
        self.contour_variation_epsilon = contour_variation_epsilon
        self.reference_distance = reference_distance
        self.absolute_distance = absolute_distance

        self.mask_bin = None
        self.mask_edge = None

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        start = time.time()
        clips = 0
        centers = []
        directions = []
        positions = []
        pixel_value = 100

        roi = None
        processed_img = frame.copy()

        # cv2.imwrite("cableFrame.png",frame)

        if frame is None:
            print("There is nothing to process")
        else:
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

            arucos = CableInspectionAlgorithm.detectArucos(frame)

            roi, coordinates = crop_roi(frame, self.graphics[0]["offset"], self.graphics[0]["bound"],
                                        self.graphics[0]["rect"], self.graphics[0]["rotation"])
            clips, centers, directions = self.detectClips(roi)

            for i in range(len(centers)):
                centers[i][0] = centers[i][0] + self.graphics[0]["bound"][0]
                centers[i][1] = centers[i][1] + self.graphics[0]["bound"][1]

            datatype = [("x", int), ("y", int), ("id", int)]
            a = np.array(arucos, datatype)
            arucos_sorted = np.sort(a, order="x")
            try:
                arucos_sorted = np.flip(arucos_sorted)

                distance_in_pixels = arucos_sorted[0][0] - arucos_sorted[1][0]

                cv2.line(frame, (arucos_sorted[0][0], arucos_sorted[0][1]),
                         (arucos_sorted[1][0], arucos_sorted[1][1]), (0, 0, 255), 2)

                pixel_value = round(self.reference_distance / distance_in_pixels, 4)

                cv2.putText(frame, "Distance in pixels: " + str(distance_in_pixels),
                            (30, 100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            2, (255, 0, 0), 8)

                cv2.putText(frame, "1 pixel value in cms: " + str(pixel_value),
                            (30, 200),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            2, (0, 255, 0), 8)
            except:
                pass

            if clips == 0:
                print("There is no clips on the cable")
                positions = [0, 0]
            else:
                if len(arucos_sorted) == 0:
                    for i in range(clips):
                        positions.append(999)
                    print(
                        "Can't tell the position of the clips on the cable since there are no ArUcos in the image")
                elif len(arucos_sorted) == 1:
                    print("The clips are ordered from left to right")
                    print("There is only one ArUco in the image")
                    for i in range(clips):
                        distance = abs(arucos_sorted[0][0] - centers[i][0])
                        print("The clip {} is {} pixels away from the ArUco.".format(i, distance))
                        distance_in_cms = distance * pixel_value
                        positions.append(distance_in_cms)
                        print("The clip {} is {} centimeters away from the ArUco.".format(i + 1, distance_in_cms))
                else:
                    for i in range(clips):
                        if self.absolute_distance is True:
                            cv2.circle(frame, (int(arucos_sorted[0][0]), int(arucos_sorted[0][1])), 12, (0, 0, 255), -1)
                            cv2.circle(frame, (int(centers[i][0]), int(centers[i][1])), 12, (0, 0, 255), -1)
                            distance = (arucos_sorted[0][0] - centers[i][0])
                            print("The clip {} is {} pixels away from the first ArUco.".format(i + 1, distance))
                            distance_in_cms = distance * pixel_value * -1
                            positions.append(distance_in_cms)
                            print(
                                "The clip {} is {} centimeters away from the ArUco.".format(i + 1, distance_in_cms))
                            cv2.putText(frame, "The clip {} is {} centimeters.".format(i + 1, distance_in_cms),
                                        (30, (500 + 100 * i)),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        2, (0, 255, 255), 8)
                            cv2.putText(frame, "The clip {} is {} pixels.".format(i + 1, distance),
                                        (30, (700 + 100 * i)),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        2, (0, 255, 255), 8)
                        else:
                            for j in range(len(arucos_sorted)):
                                if centers[i][0] > arucos_sorted[j][0]:
                                    if j == 0:
                                        distance = abs(centers[i][0] - arucos_sorted[j][0])
                                        print("The first ArUco detected is on the left side of the clip {} and "
                                              "there are {} pixels between them.".format(i + 1, distance))
                                        distance_in_cms = distance * pixel_value
                                        positions.append(distance_in_cms)
                                        print("The clip {} is {} centimeters away from the ArUco."
                                              .format(i + 1, distance_in_cms))
                                    else:
                                        distance = abs(centers[i][0] - arucos_sorted[j - 1][0])
                                        print(
                                            "The clip {} is {} pixels away from the first ArUco on its right side."
                                                .format(i + 1, distance))
                                        distance_in_cms = (distance * pixel_value) + (
                                                (j - 1) * self.reference_distance)
                                        positions.append(distance_in_cms)
                                        print(
                                            "The clip {} is {} centimeters away from the right end of the cable."
                                                .format(i + 1, distance_in_cms))
                                    break

            processed_img = cv2.rectangle(frame.copy(), (coordinates[0], coordinates[1]), (coordinates[2], coordinates[3]),
                                          (255, 0, 0), 5)

        self.algorithm_result.data = {
            "clipsCount": clips,
            "positions": positions,
            "centers": centers,
            "directions": directions,
            "pixelValue": pixel_value
        }

        print("CableInspectionAlg:", self.algorithm_result.data)
        self.mask_bin = cv2.cvtColor(self.mask_bin, cv2.COLOR_GRAY2BGR)
        self.mask_edge = cv2.cvtColor(self.mask_edge, cv2.COLOR_GRAY2BGR)

        if roi is None:
            roi = np.zeros(shape=self.mask_bin, dtype=np.uint8)

        vis = np.concatenate((roi, self.mask_bin, self.mask_edge), axis=1)
        self.algorithm_result.listSave = [frame, roi, self.mask_bin]
        self.algorithm_result.imageRoi = vis
        self.algorithm_result.debugImages = [processed_img, frame]
        print("self.graphics[0]", self.graphics[0])
        self.algorithm_result.roiCoordinates = self.graphics[0]
        time2 = time.time()
        print('\033[92m' + "CLIPS:::" + '\033[0m', time2 - start)
        return self.algorithm_result

    def detectClips(self, frame: np.ndarray):
        contours_match = False
        pos = c1 = c2 = c3 = c4 = None
        clips_count = 0
        clips_centers = []
        clips_orientation = []
        if frame is None:
            print("There is nothing to process")
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.blur(gray, (self.blur_kernel_size, self.blur_kernel_size))

            if self.bin_upper_threshold == 255:
                ret, mask = cv2.threshold(blur, self.bin_lower_threshold, self.bin_upper_threshold,
                                          cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            else:
                ret, mask = cv2.threshold(blur, self.bin_lower_threshold, 255,
                                          cv2.THRESH_BINARY)

            self.mask_bin = mask
            edged = cv2.Canny(mask, self.canny_first_threshold, self.canny_second_threshold)
            self.mask_edge = edged

            kernel = np.ones((5, 5), np.uint8)

            edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

            contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            # order the contours by their size in descending order,
            # the 2 sides of the cable will be the first 2 contours
            contours_ordered = self.orderContoursBySize(contours)

            if len(contours_ordered) < 2:
                print("Didn't find the sides of the cable in the image")
            else:
                ordered_on_y = self.orderFromTopToBottom(contours_ordered[0], contours_ordered[1])

                clip_peaks_fc = []
                clip_peaks_sc = []

                x1 = x2 = x3 = x4 = y1 = y2 = y3 = y4 = None
                contours_match = True

                clip_position_fc = []
                clip_position_sc = []

                clips_line_params_fc = []
                clips_line_params_sc = []

                for i in range(2):
                    cnt = ordered_on_y[i]
                    frame = cv2.drawContours(frame, cnt, -1, (0, 0, 0), 3)

                    # order the contour points in ascending order on the x axis
                    # datatype = [("x", int), ("y", int)]
                    # cnt_as_tuple_array = self.convertNumpyArrToTupleArray(cnt)
                    # np_array = np.array(cnt_as_tuple_array, datatype)
                    # sorted_cnt = np.sort(np_array, order="x")

                    sorted_cnt = cnt[cnt[:, 0, 0].argsort()]

                    # flatten the sorted contour

                    flattened_contour = self.flattenContour(sorted_cnt, self.flatten_contour_step)
                    flattened_contour = flattened_contour.astype(int)

                    # np_array = np.array(flattened_contour, datatype)
                    # # sort the flattened contour
                    # flat_sorted = np.sort(np_array, order="x")

                    flat_sorted = flattened_contour[flattened_contour[:, 0, 0].argsort()]

                    flat_connected, x_start, y_start, x_stop, y_stop = self.connectContour(flat_sorted)

                    frame = cv2.drawContours(frame, flat_connected, -1, (0, 0, 255), 3)

                    original_contour = np.unique(sorted_cnt, axis=0)
                    flat_contour = np.unique(flat_connected, axis=0)
                    # flat_contour = np.sort(flat_contour, order="x")
                    flat_contour = flat_contour[flat_contour[:, 0, 0].argsort()]

                    if len(flat_contour) != len(original_contour):
                        contours_match = False

                    for j in range(len(x_start)):
                        a = (y_stop[j] - y_start[j]) * -1
                        b = x_stop[j] - x_start[j]
                        c = (y_start[j] * (x_stop[j] - x_start[j]) + x_start[j] * (y_start[j] - y_stop[j])) * -1

                        indices_start_orig = np.where(original_contour == x_start[j])
                        indices_stop_orig = np.where(original_contour == x_stop[j])
                        indices_start_flat = np.where(flat_contour == x_start[j])
                        indices_stop_flat = np.where(flat_contour == x_stop[j])

                        start_orig = stop_orig = start_flat = stop_flat = None
                        for t in indices_start_orig[0]:
                            if original_contour[t][0][0] == x_start[j]:
                                start_orig = t

                        for t in indices_stop_orig[0]:
                            if original_contour[t][0][0] == x_stop[j]:
                                stop_orig = t

                        for t in indices_start_flat[0]:
                            if flat_contour[t][0][0] == x_start[j]:
                                start_flat = t

                        for t in indices_stop_flat[0]:
                            if flat_contour[t][0][0] == x_stop[j]:
                                stop_flat = t

                        min_orig = max_orig = min_flat = max_flat = None
                        if start_orig is not None and stop_orig is not None and start_flat is not None \
                                and stop_flat is not None:
                            min_orig = min(start_orig, stop_orig)
                            max_orig = max(start_orig, stop_orig)
                            min_flat = min(start_flat, stop_flat)
                            max_flat = max(start_flat, stop_flat)

                        if i == 0:
                            if min_orig is not None and max_orig is not None and min_flat is not None \
                                    and max_flat is not None:
                                (x1, y1) = self.findClipsPosition(original_contour[min_orig:max_orig],
                                                                  flat_contour[min_flat:max_flat], first=True)
                                (x3, y3) = self.findClipsPosition(np.flip(original_contour[min_orig:max_orig], axis=0),
                                                                  np.flip(flat_contour[min_flat:max_flat], axis=0),
                                                                  first=True)
                                if x1 is not None and x3 is not None:
                                    clip_position_fc.append((x1, y1, x3, y3))
                        else:
                            if min_orig is not None and max_orig is not None and min_flat is not None \
                                    and max_flat is not None:
                                (x2, y2) = self.findClipsPosition(original_contour[min_orig:max_orig],
                                                                  flat_contour[min_flat:max_flat], first=False)
                                (x4, y4) = self.findClipsPosition(np.flip(original_contour[min_orig:max_orig], axis=0),
                                                                  np.flip(flat_contour[min_flat:max_flat], axis=0),
                                                                  first=False)
                                if x2 is not None and x4 is not None:
                                    clip_position_sc.append((x2, y2, x4, y4))

                        if min_orig is not None and max_orig is not None:
                            clip_area = original_contour[min_orig:max_orig]
                            # np_array = np.array(clip_area, datatype)
                            # cnt_sorted_on_y = np.sort(np_array, order="y")
                            cnt_sorted_on_y = clip_area[clip_area[:, 0, 1].argsort()]

                            if i == 0:
                                if x1 is not None:
                                    clip_peaks_fc.append((cnt_sorted_on_y[0][0][0], cnt_sorted_on_y[0][0][1]))
                                    clips_line_params_fc.append((a, b, c))
                            else:
                                if x2 is not None:
                                    clip_peaks_sc.append((cnt_sorted_on_y[len(cnt_sorted_on_y) - 1][0][0],
                                                          cnt_sorted_on_y[len(cnt_sorted_on_y) - 1][0][1]))
                                    clips_line_params_sc.append((a, b, c))

                # print("first contour initially " + str(clip_position_fc))
                # print("second contour initially " + str(clip_position_sc))

                # print("first contour peaks initially " + str(clip_peaks_fc))
                # print("second contour peaks initially " + str(clip_peaks_sc))

                sc_indexes = []
                fc_indexes = []

                for i in range(min(len(clip_position_fc), len(clip_position_sc))):
                    if clip_position_sc[i][0] is not None and clip_position_sc[i][2] is not None and \
                            clip_position_fc[i][0] is not None and clip_position_fc[i][2] is not None:
                        if abs(clip_position_fc[i][0] - clip_position_fc[i][2]) > abs(
                                clip_position_sc[i][0] - clip_position_sc[i][2]):
                            if not (clip_position_fc[i][0] <= clip_position_sc[i][0] <= clip_position_fc[i][
                                2]) and not (
                                    clip_position_fc[i][0] <= clip_position_sc[i][2] <= clip_position_fc[i][2]):
                                if clip_position_fc[i][0] < clip_position_sc[i][0]:
                                    sc_indexes.append(i)
                                    fc_indexes.append(i + 1)
                                else:
                                    sc_indexes.append(i + 1)
                                    fc_indexes.append(i)
                        else:
                            if not (clip_position_sc[i][0] <= clip_position_fc[i][0] <= clip_position_sc[i][
                                2]) and not (
                                    clip_position_sc[i][0] <= clip_position_fc[i][2] <= clip_position_sc[i][2]):
                                if clip_position_fc[i][0] < clip_position_sc[i][0]:
                                    sc_indexes.append(i)
                                    fc_indexes.append(i + 1)
                                else:
                                    sc_indexes.append(i + 1)
                                    fc_indexes.append(i)

                for i in fc_indexes:
                    clip_position_fc.insert(i, (None, None, None, None))
                    clip_peaks_fc.insert(i, (None, None))
                    clips_line_params_fc.insert(i, None)

                for i in sc_indexes:
                    clip_position_sc.insert(i, (None, None, None, None))
                    clip_peaks_sc.insert(i, (None, None))
                    clips_line_params_sc.insert(i, None)

                while len(clip_position_fc) != len(clip_position_sc):
                    if len(clip_position_fc) < len(clip_position_sc):
                        clip_position_fc.append((None, None, None, None))
                        clip_peaks_fc.append((None, None))
                        clips_line_params_fc.append(None)
                    else:
                        clip_position_sc.append((None, None, None, None))
                        clip_peaks_sc.append((None, None))
                        clips_line_params_sc.append(None)

                # print("first contour " + str(clip_position_fc))
                # print("second contour " + str(clip_position_sc))

                # print("first contour peaks " + str(clip_peaks_fc))
                # print("second contour peaks " + str(clip_peaks_sc))

                if contours_match is False:
                    if len(clip_position_fc) == 0 and len(clip_position_sc) == 0:
                        print("Nothing found on the cable!")
                        return clips_count, clips_centers, []
                    else:
                        clips_count = max(len(clip_position_fc), len(clip_position_sc))
                        for i in range(clips_count):
                            if clip_position_fc[i][0] is None:
                                c1 = [[clip_position_sc[i][0], clip_position_sc[i][1]]]
                                c2 = [[clip_position_sc[i][2], clip_position_sc[i][3]]]
                                c3 = [[clip_position_sc[i][2], clip_peaks_sc[i][1]]]
                                c4 = [[clip_position_sc[i][0], clip_peaks_sc[i][1]]]

                                clips_orientation.append("down")

                                cv2.line(frame, (c1[0][0], c1[0][1]),
                                         (c2[0][0], c2[0][1]), (0, 255, 0), 2)
                                cv2.line(frame, (c2[0][0], c2[0][1]),
                                         (c3[0][0], c3[0][1]), (0, 255, 0), 2)
                                cv2.line(frame, (c3[0][0], c3[0][1]),
                                         (c4[0][0], c4[0][1]), (0, 255, 0), 2)
                                cv2.line(frame, (c4[0][0], c4[0][1]),
                                         (c1[0][0], c1[0][1]), (0, 255, 0), 2)
                            elif clip_position_sc[i][0] is None:
                                c4 = [[clip_position_fc[i][0], clip_position_fc[i][1]]]
                                c3 = [[clip_position_fc[i][2], clip_position_fc[i][3]]]
                                c2 = [[clip_position_fc[i][2], clip_peaks_fc[i][1]]]
                                c1 = [[clip_position_fc[i][0], clip_peaks_fc[i][1]]]

                                clips_orientation.append("up")

                                cv2.line(frame, (c1[0][0], c1[0][1]),
                                         (c2[0][0], c2[0][1]), (0, 255, 0), 2)
                                cv2.line(frame, (c2[0][0], c2[0][1]),
                                         (c3[0][0], c3[0][1]), (0, 255, 0), 2)
                                cv2.line(frame, (c3[0][0], c3[0][1]),
                                         (c4[0][0], c4[0][1]), (0, 255, 0), 2)
                                cv2.line(frame, (c4[0][0], c4[0][1]),
                                         (c1[0][0], c1[0][1]), (0, 255, 0), 2)
                            else:
                                c1 = [[clip_position_fc[i][0], clip_peaks_fc[i][1]]]
                                c2 = [[clip_position_fc[i][2], clip_peaks_fc[i][1]]]
                                c3 = [[clip_position_sc[i][2], clip_peaks_sc[i][1]]]
                                c4 = [[clip_position_sc[i][0], clip_peaks_sc[i][1]]]

                                x_middle_up = int((c1[0][0] + c2[0][0]) / 2)
                                y_middle_up = int((c1[0][1] + c2[0][1]) / 2)

                                x_middle_down = int((c3[0][0] + c4[0][0]) / 2)
                                y_middle_down = int((c3[0][1] + c4[0][1]) / 2)

                                upper_clips = abs(clips_line_params_fc[i][0] * x_middle_up + clips_line_params_fc[i][1]
                                                  * y_middle_up + clips_line_params_fc[i][2]) / \
                                              math.sqrt(
                                                  clips_line_params_fc[i][0] ** 2 + clips_line_params_fc[i][1] ** 2)

                                lower_clips = abs(
                                    clips_line_params_sc[i][0] * x_middle_down + clips_line_params_sc[i][1]
                                    * y_middle_down + clips_line_params_sc[i][2]) / \
                                              math.sqrt(
                                                  clips_line_params_sc[i][0] ** 2 + clips_line_params_sc[i][1] ** 2)

                                if upper_clips > lower_clips:
                                    clips_orientation.append("up")
                                else:
                                    clips_orientation.append("down")

                                # if abs(clip_position_fc[i][1] - clip_peaks_fc[i][1]) > abs(
                                #         clip_position_sc[i][1] - clip_peaks_sc[i][1]):
                                #     clips_orientation.append("up")
                                # else:
                                #     clips_orientation.append("down")

                                cv2.line(frame, (c1[0][0], c1[0][1]),
                                         (c2[0][0], c2[0][1]), (0, 255, 0), 2)
                                cv2.line(frame, (c2[0][0], c2[0][1]),
                                         (c3[0][0], c3[0][1]), (0, 255, 0), 2)
                                cv2.line(frame, (c3[0][0], c3[0][1]),
                                         (c4[0][0], c4[0][1]), (0, 255, 0), 2)
                                cv2.line(frame, (c4[0][0], c4[0][1]),
                                         (c1[0][0], c1[0][1]), (0, 255, 0), 2)

                            x_center = c1[0][0] + int((c2[0][0] - c1[0][0]) / 2)
                            y_center = c2[0][1] + int((c3[0][1] - c2[0][1]) / 2)

                            # area = cv2.contourArea(np.array([c1, c2, c3, c4]))
                            #
                            # a = CableInspectionAlgorithm.dist(c1[0], c2[0])
                            # b = CableInspectionAlgorithm.dist(c4[0], c3[0])
                            # c = CableInspectionAlgorithm.dist(c1[0], c4[0])
                            # d = CableInspectionAlgorithm.dist(c2[0], c3[0])
                            #
                            # height = (2 * area) / (a + b)
                            #
                            # y = int(((b + 2 * a) / (3 * (a + b))) * height)
                            # x = int((b / 2) + ((2 * a + b) * (c * c - d * d) / (6 * (b * b - a * a))))
                            #
                            # x_center = c4[0][0] + x
                            # y_center = c4[0][1] - y

                            clips_centers.append([x_center, y_center])
                else:
                    print("Absent")

        return clips_count, clips_centers, clips_orientation

    @staticmethod
    def dist(pt1, pt2):
        return math.sqrt((pt2[0] - pt1[0]) ** 2 + (pt2[1] - pt1[1]) ** 2)

    @staticmethod
    def orderContoursBySize(contours: list):
        perimeters = []
        contours_ordered = []
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            perimeters.append(perimeter)

        for i in range(len(perimeters)):
            max_value = max(perimeters)
            pos = perimeters.index(max_value)
            contours_ordered.append(contours[pos])
            perimeters[pos] = -1.0

        return contours_ordered

    @staticmethod
    def orderFromTopToBottom(contour1: list, contour2: list):
        (x1, y1), (x2, y2) = CableInspectionAlgorithm.findExtremePoints(contour1, 0)
        (x3, y3), (x3, y4) = CableInspectionAlgorithm.findExtremePoints(contour2, 0)

        if y1 < y3:
            return [contour1, contour2]

        return [contour2, contour1]

    @staticmethod
    def findExtremePoints(contour: list, axis):

        col_max = np.amax(contour, axis=axis)
        max_x = col_max[0][axis]
        col_min = np.amin(contour, axis=axis)
        min_x = col_min[0][axis]

        min_indices = np.where(contour == min_x)
        max_indices = np.where(contour == max_x)

        left_x = contour[min_indices[0]][0][0][0]
        left_y = contour[min_indices[0]][0][0][1]
        right_x = contour[max_indices[0]][0][0][0]
        right_y = contour[max_indices[0]][0][0][1]

        return (left_x, left_y), (right_x, right_y)

    @staticmethod
    def convertNumpyArrToTupleArray(array: list):
        output = []
        for i in range(len(array)):
            x = array[i][0][0]
            y = array[i][0][1]
            elem = (x, y)
            output.append(elem)

        return output

    @staticmethod
    def convertListOfTuplesToNumpy(array: np.ndarray):
        output = []
        for i in range(len(array)):
            (x, y) = array[i]
            elem = [[x, y]]
            output.append(elem)

        return output

    def flattenContour(self, contour: np.ndarray, step: int):
        hill_count = 0
        hill = False
        slope = 0
        x3 = y3 = None
        flattened_contour = np.empty((len(contour), 1, 2))
        elem_index = 0

        for i in range(0, len(contour), step):
            x1 = contour[i][0][0]
            y1 = contour[i][0][1]
            s = None
            if i + step > len(contour) - 1:
                s = len(contour) - 1 - i
            else:
                s = step
            x2 = contour[i + s][0][0]
            y2 = contour[i + s][0][1]
            if x1 == x2:
                if y1 == y2:
                    continue
            else:
                slope = (y1 - y2) / (x1 - x2)
                angle = math.degrees(math.atan(slope))
                angle = abs(angle)
                if angle > self.threshold_angle:
                    hill_count += 1
                    hill = True
                    if hill_count == 1:
                        x3 = x1
                        y3 = y1
                else:
                    if hill is True:
                        base_slope = (y3 - y2) / (x3 - x2)
                        base_angle = math.degrees(math.atan(base_slope))
                        base_angle = abs(base_angle)
                        if base_angle > self.threshold_angle:
                            hill = True
                        else:
                            hill = False
                            hill_count = 0
                    else:
                        std = np.std(contour[i:i + s + 1], 0)
                        if std[0][1] < 10 and hill is False:
                            if i + step >= len(contour) - 1:
                                stop = i + s + 1
                            else:
                                stop = i + s
                            for p in range(i, stop):
                                flattened_contour[elem_index][0] = np.array([[contour[p][0][0], contour[p][0][1]]])
                                elem_index += 1

        return flattened_contour[:elem_index]

    @staticmethod
    def connectContour(contour: np.ndarray):
        x_start = []
        y_start = []
        x_stop = []
        y_stop = []
        output_contour = contour

        for i in range(len(contour) - 1):
            if abs(contour[i + 1][0][0] - contour[i][0][0]) > 2:
                x_start.append(contour[i][0][0])
                y_start.append(contour[i][0][1])
                x_stop.append(contour[i + 1][0][0])
                y_stop.append(contour[i + 1][0][1])
                slope = (contour[i + 1][0][1] - contour[i][0][1]) / (contour[i + 1][0][0] - contour[i][0][0])
                c = contour[i][0][1] - contour[i][0][0] * slope
                for j in range(min(contour[i + 1][0][0], contour[i][0][0]),
                               max(contour[i + 1][0][0], contour[i][0][0])):
                    y = slope * j + c
                    elem = np.array([[[j, int(y)]]])
                    output_contour = np.concatenate((output_contour, elem))

        return output_contour, x_start, y_start, x_stop, y_stop

    def findClipsPosition(self, original_contour: np.ndarray, flattened_contour: np.ndarray, first=True):
        x1 = y1 = None
        for i in range(len(flattened_contour)):
            if first is True:
                contour_difference = flattened_contour[i][0][1] - self.contour_variation_epsilon > original_contour[i][0][
                    1]
            else:
                contour_difference = original_contour[i][0][1] > flattened_contour[i][0][
                    1] + self.contour_variation_epsilon

            if contour_difference:
                x1 = original_contour[i][0][0]
                y1 = original_contour[i][0][1]
                break
            else:
                continue

            # if flattened_contour[i][0][1] - self.contourVariationEpsilon < original_contour[i][0][1] < \
            #         flattened_contour[i][0][1] + self.contourVariationEpsilon:
            #     continue
            # else:
            #     x1 = original_contour[i][0][0]
            #     y1 = original_contour[i][0][1]
            #     break

        return x1, y1

    @staticmethod
    def detectArucos(frame: np.ndarray):
        aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        aruco_params = cv2.aruco.DetectorParameters_create()
        (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=aruco_params)
        arucos = []
        # verify *at least* one ArUco marker was detected
        if len(corners) > 0:
            # flatten the ArUco IDs list
            ids = ids.flatten()
            # loop over the detected ArUCo corners
            for (marker_corner, marker_id) in zip(corners, ids):
                corners = marker_corner.reshape((4, 2))
                (top_left, top_right, bottom_right, bottom_left) = corners
                # convert each of the (x, y)-coordinate pairs to integers
                top_right = (int(top_right[0]), int(top_right[1]))
                bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
                bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
                top_left = (int(top_left[0]), int(top_left[1]))

                # draw the bounding box of the ArUCo detection
                cv2.line(frame, top_left, top_right, (0, 255, 0), 2)
                cv2.line(frame, top_right, bottom_right, (0, 255, 0), 2)
                cv2.line(frame, bottom_right, bottom_left, (0, 255, 0), 2)
                cv2.line(frame, bottom_left, top_left, (0, 255, 0), 2)
                # compute and draw the center (x, y)-coordinates of the ArUco
                # marker
                cX = int((top_left[0] + bottom_right[0]) / 2.0)
                cY = int((top_left[1] + bottom_right[1]) / 2.0)
                # cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
                arucos.append((cX, cY, marker_id))
                # draw the ArUco marker ID on the image
                cv2.putText(frame, str(marker_id),
                            (top_left[0], top_left[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 2)

        return arucos
