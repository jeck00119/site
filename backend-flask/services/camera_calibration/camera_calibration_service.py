from typing import Union

import cv2
import numpy as np

from repo.repositories import CameraCalibrationRepository
from services.camera_calibration.camera_calibration_models import CameraCalibrationParametersModel, \
    CameraIntrinsicsModel
from src.metaclasses.singleton import Singleton


class CameraCalibrationService(metaclass=Singleton):
    def __init__(self):
        self.camera_calibration_repository: CameraCalibrationRepository = CameraCalibrationRepository()
        self.current_calibration_parameters: Union[None, CameraCalibrationParametersModel] = None
        self.calibration_frames = []

        self.camera_matrix = None
        self.distortion_coeffs = None

        self.rmse = None

    def set_calibration_parameters(self, calibration_parameters: CameraCalibrationParametersModel):
        self.current_calibration_parameters = calibration_parameters
        self.calibration_frames.clear()

    def save_calibration_frame(self, frame):
        self.calibration_frames.append(frame)

    def calibrate_camera(self):
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)

        rows = self.current_calibration_parameters.rows
        columns = self.current_calibration_parameters.cols
        world_scaling = self.current_calibration_parameters.square_size

        # coordinates of squares in the checkerboard world space
        objp = np.zeros((rows * columns, 3), np.float32)
        objp[:, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)
        objp = world_scaling * objp

        # frame dimensions. Frames should be the same size.
        width = self.calibration_frames[0].shape[1]
        height = self.calibration_frames[0].shape[0]

        # Pixel coordinates of checkerboards
        imgpoints = []  # 2d points in image plane.

        # coordinates of the checkerboard in checkerboard world space.
        objpoints = []  # 3d point in real world space

        for i, frame in enumerate(self.calibration_frames):
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # find the checkerboard
            ret, corners = cv2.findChessboardCorners(gray, (rows, columns), None)

            if ret is True:
                # Convolution size used to improve corner detection. Don't make this too large.
                conv_size = (11, 11)

                # opencv2 can attempt to improve the checkerboard coordinates
                corners = cv2.cornerSubPix(gray, corners, conv_size, (-1, -1), criteria)
                cv2.drawChessboardCorners(frame, (rows, columns), corners, ret)

                objpoints.append(objp)
                imgpoints.append(corners)

        ret, cmtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (width, height), None, None)
        self.camera_matrix = cmtx
        self.distortion_coeffs = dist
        self.rmse = ret

    def undistort_image(self, frame, uid):
        calibration = self.camera_calibration_repository.read_id(uid)

        calibration = self.camera_calibration_repository.convert_dict_to_model(calibration)

        camera_matrix = np.array(calibration.camera_matrix)
        dist_coeffs = np.array(calibration.distortion_coeffs)

        h, w = frame.shape[:2]

        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

        dst = cv2.undistort(frame, camera_matrix, dist_coeffs, None, new_camera_matrix)

        # crop the image
        x, y, w, h = roi
        dst = dst[y:y + h, x:x + w]

        return dst

    def get_calibration_frame(self, idx):
        return self.calibration_frames[idx]

    def save_calibration_results(self, uid: str):
        camera_calibration_model = CameraIntrinsicsModel(uid=uid, camera_matrix=self.camera_matrix.tolist(),
                                                         distortion_coeffs=self.distortion_coeffs.tolist())
        self.camera_calibration_repository.create(camera_calibration_model)

    def get_rmse(self):
        return self.rmse

    def delete_calibration(self, uid: str):
        self.camera_calibration_repository.delete(uid)
