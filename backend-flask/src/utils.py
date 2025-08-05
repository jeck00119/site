import base64
import json
import string
from typing import List

import cv2
import imutils as imutils
import numpy as np
import shortuuid
from humps.camel import case
from pydantic import BaseModel, ConfigDict

alphabet = string.ascii_lowercase + string.digits
su = shortuuid.ShortUUID(alphabet=alphabet)


def to_camel(string):
    return case(string)


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @staticmethod
    def load_ui_dictionary(file_name):
        with open(file_name) as f:
            data = json.load(f)

        return data


def frame_to_base64(frame):
    retval, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer)
    return jpg_as_text


def generate_uid(length: int = 8):
    return su.random(length=length)


def generate_uid_camera_settings():
    return su.random(length=6)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def crop_roi(frame: np.ndarray, roi_offset: List[float], roi_bound: List[float],
             roi_rect: List[float], rotation: int = 0, offset: int = 0):
    height = frame.shape[0]
    width = frame.shape[1]

    b_x1 = int(roi_bound[0]) - offset
    b_x2 = int(roi_bound[0] + roi_bound[2]) + 2 * offset
    b_y1 = int(roi_bound[1]) - offset
    b_y2 = int(roi_bound[1] + roi_bound[3]) + 2 * offset

    roi = frame[b_y1:b_y2, b_x1:b_x2]

    roi = imutils.rotate_bound(roi, -rotation)

    x1 = int(roi_offset[0]) - offset
    x2 = int(roi_offset[0] + roi_rect[2]) + 2 * offset
    y1 = int(roi_offset[1]) - offset
    y2 = int(roi_offset[1] + roi_rect[3]) + 2 * offset

    if x1 < 0:
        x1 = 0
    if x2 > roi.shape[1] - 1:
        x2 = roi.shape[1] - 1
    if y1 < 0:
        y1 = 0
    if y2 > roi.shape[0] - 1:
        y2 = roi.shape[0] - 1

    roi = roi[y1:y2, x1:x2]
    return roi, [b_x1, b_y1, b_x2, b_y2]


def adjust_gamma(image, gamma=1.0):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")

    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)


def detect_arucos(frame, dictionary):
    aruco_dict = cv2.aruco.Dictionary_get(dictionary)

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
            cx = int((top_left[0] + bottom_right[0]) / 2.0)
            cy = int((bottom_right[1] + bottom_right[1]) / 2.0)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
            arucos.append({'x': cx, 'y': cy, 'id': int(marker_id), 'topLeft': top_left, 'bottomRight': bottom_right})

            # draw the ArUco marker ID on the image
            cv2.putText(frame, str(marker_id),
                        (top_left[0], top_left[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)

    return arucos


def hex_to_rgb(hexadecimal: str):
    if len(hexadecimal) != 7 or hexadecimal.find('#'):
        return None

    r = int(hexadecimal[1:3], 16)
    g = int(hexadecimal[3:5], 16)
    b = int(hexadecimal[5:], 16)

    return r, g, b


def split_rectangle_in_4(image, top_left_corner, width, height):
    top_left = image[top_left_corner[1]:top_left_corner[1] + int(height / 2),
                     top_left_corner[0]:top_left_corner[0] + int(width / 2)]
    top_right = image[top_left_corner[1]:top_left_corner[1] + int(height / 2),
                      top_left_corner[0] + int(width / 2):top_left_corner[0] + int(width)]
    bottom_left = image[top_left_corner[1] + int(height / 2):top_left_corner[1] + int(height),
                        top_left_corner[0]:top_left_corner[0] + int(width / 2)]
    bottom_right = image[top_left_corner[1] + int(height / 2):top_left_corner[1] + int(height),
                         top_left_corner[0] + int(width / 2):top_left_corner[0] + int(width)]

    return [top_left, top_right, bottom_left, bottom_right]
