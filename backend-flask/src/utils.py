import base64
import json
import string
import logging
from typing import List, Optional

import cv2
import imutils as imutils
import numpy as np
import shortuuid
from humps.camel import case
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)

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


def frame_to_base64(frame, quality: int = 95, format: str = '.jpg'):
    """
    Convert frame to base64 encoded string with proper error handling and validation.
    
    Args:
        frame: OpenCV image frame (numpy array)
        quality: JPEG quality (1-100, default 95)
        format: Image format ('.jpg', '.png', default '.jpg')
    
    Returns:
        bytes: Base64 encoded image data
    
    Raises:
        ValueError: If frame is invalid or encoding fails
        TypeError: If frame is not a numpy array
    """
    # Validate input frame
    if frame is None:
        raise ValueError("Frame cannot be None")
    
    if not isinstance(frame, np.ndarray):
        raise TypeError(f"Frame must be numpy array, got {type(frame)}")
    
    if frame.size == 0:
        raise ValueError("Frame cannot be empty")
    
    # Validate and clamp quality for JPEG
    if format.lower() == '.jpg':
        quality = max(1, min(100, quality))
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    else:
        encode_params = []
    
    # Encode frame with error checking
    retval, buffer = cv2.imencode(format, frame, encode_params)
    
    if not retval or buffer is None or buffer.size == 0:
        raise ValueError(f"Failed to encode frame to {format} format")
    
    # Convert to base64
    try:
        jpg_as_text = base64.b64encode(buffer)
        return jpg_as_text
    except Exception as e:
        raise ValueError(f"Failed to encode frame to base64: {str(e)}")


def load_fallback_image(fallback_path: str = 'assets/no_camera.jpg', 
                       width: int = 640, height: int = 480) -> np.ndarray:
    """
    Centralized fallback image loading with consistent error handling.
    
    Args:
        fallback_path: Path to fallback image file
        width: Width for generated placeholder if file loading fails
        height: Height for generated placeholder if file loading fails
    
    Returns:
        numpy.ndarray: Fallback image or generated placeholder
    """
    try:
        image = cv2.imread(fallback_path)
        if image is not None:
            logger.debug(f"Successfully loaded fallback image: {fallback_path}")
            return image
        else:
            logger.warning(f"Failed to load fallback image from {fallback_path}, generating placeholder")
    except Exception as e:
        logger.error(f"Error loading fallback image {fallback_path}: {e}")
    
    # Generate consistent placeholder image
    try:
        placeholder = np.full((height, width, 3), 128, dtype=np.uint8)
        logger.debug(f"Generated {width}x{height} placeholder image")
        return placeholder
    except Exception as e:
        logger.error(f"Failed to generate placeholder image: {e}")
        # Last resort - minimal 1x1 gray image
        return np.full((1, 1, 3), 128, dtype=np.uint8)


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
