from typing import Union

import cv2
import numpy as np

from repo.repositories import StereoCalibrationRepository
from services.camera_calibration.camera_calibration_models import CameraCalibrationParametersModel
from services.stereo_calibration.stereo_calibration_models import StereoResultsModel
from src.metaclasses.singleton import Singleton


class StereoCalibrationService(metaclass=Singleton):
    def __init__(self):
        self.stereo_calibration_repository: StereoCalibrationRepository = StereoCalibrationRepository()
        self.current_calibration_parameters: Union[None, CameraCalibrationParametersModel] = None
        self.calibration_frames_first_src = []
        self.calibration_frames_second_src = []

        self.rotation = None
        self.translation = None
        self.essential_matrix = None
        self.fundamental_matrix = None

        self.rmse = None

    def set_calibration_parameters(self, calibration_parameters: CameraCalibrationParametersModel):
        self.current_calibration_parameters = calibration_parameters
        self.calibration_frames_first_src.clear()
        self.calibration_frames_second_src.clear()

    def save_calibration_frame_pair(self, frame1, frame2):
        self.calibration_frames_first_src.append(frame1)
        self.calibration_frames_second_src.append(frame2)

    def stereo_calibrate(self, cam_mtx1, dist1, cam_mtx2, dist2):
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)

        # calibration pattern settings
        rows = self.current_calibration_parameters.rows
        columns = self.current_calibration_parameters.cols
        world_scaling = self.current_calibration_parameters.square_size

        # coordinates of squares in the checkerboard world space
        objp = np.zeros((rows * columns, 3), np.float32)
        objp[:, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)
        objp = world_scaling * objp

        # frame dimensions. Frames should be the same size.
        width = self.calibration_frames_first_src[0].shape[1]
        height = self.calibration_frames_first_src[0].shape[0]

        # Pixel coordinates of checkerboards
        imgpoints_left = []  # 2d points in image plane.
        imgpoints_right = []

        # coordinates of the checkerboard in checkerboard world space.
        objpoints = []  # 3d point in real world space

        for frame0, frame1 in zip(self.calibration_frames_first_src, self.calibration_frames_second_src):
            gray1 = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            c_ret1, corners1 = cv2.findChessboardCorners(gray1, (rows, columns), None)
            c_ret2, corners2 = cv2.findChessboardCorners(gray2, (rows, columns), None)

            if c_ret1 == True and c_ret2 == True:

                corners1 = cv2.cornerSubPix(gray1, corners1, (11, 11), (-1, -1), criteria)
                corners2 = cv2.cornerSubPix(gray2, corners2, (11, 11), (-1, -1), criteria)

                p0_c1 = corners1[0, 0].astype(np.int32)
                p0_c2 = corners2[0, 0].astype(np.int32)

                cv2.putText(frame0, 'O', (p0_c1[0], p0_c1[1]), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)
                cv2.drawChessboardCorners(frame0, (rows, columns), corners1, c_ret1)

                cv2.putText(frame1, 'O', (p0_c2[0], p0_c2[1]), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)
                cv2.drawChessboardCorners(frame1, (rows, columns), corners2, c_ret2)

                objpoints.append(objp)
                imgpoints_left.append(corners1)
                imgpoints_right.append(corners2)

        stereocalibration_flags = cv2.CALIB_FIX_INTRINSIC
        ret, CM1, dist0, CM2, dist1, R, T, E, F = cv2.stereoCalibrate(objpoints, imgpoints_left, imgpoints_right,
                                                                      cam_mtx1,
                                                                      dist1,
                                                                      cam_mtx2, dist2, (width, height),
                                                                      criteria=criteria,
                                                                      flags=stereocalibration_flags)

        self.rotation = R
        self.translation = T
        self.essential_matrix = E
        self.fundamental_matrix = F

        self.rmse = ret

    def get_calibration_frame_pair(self, idx):
        return self.calibration_frames_first_src[idx], self.calibration_frames_second_src[idx]

    def save_calibration_results(self, uid: str, first_img_src_uid: str, second_img_src_uid: str):
        q = Query()
        calibration = self.stereo_calibration_repository.find_by_query((q.first_image_src_uid == first_img_src_uid) & (
                                q.second_image_src_uid == second_img_src_uid))

        if calibration:
            print(calibration)
            self.stereo_calibration_repository.delete(calibration[0]["uid"])

        stereo_results_model = StereoResultsModel(uid=uid, first_image_src_uid=first_img_src_uid,
                                                  second_image_src_uid=second_img_src_uid,
                                                  R0=np.eye(3, dtype=np.float32).tolist(),
                                                  T0=np.array([0., 0., 0.]).reshape((3, 1)).tolist(),
                                                  R1=self.rotation.tolist(),
                                                  T1=self.translation.tolist(),
                                                  world_to_cam_left_rot=None,
                                                  world_to_cam_left_trans=None,
                                                  world_to_cam_right_rot=None,
                                                  world_to_cam_right_trans=None,
                                                  essential_matrix=self.essential_matrix.tolist(),
                                                  fundamental_matrix=self.fundamental_matrix.tolist())
        self.stereo_calibration_repository.create(stereo_results_model)

    def get_rmse(self):
        return self.rmse

    def set_world_frame_origin(self, left_frame, right_frame, left_camera_matrix, left_camera_distortion,
                               right_camera_matrix, right_camera_distortion):
        R1 = self.rotation
        T1 = self.translation
        rows = self.current_calibration_parameters.rows
        columns = self.current_calibration_parameters.cols
        world_scaling = self.current_calibration_parameters.square_size
        # coordinates of squares in the checkerboard world space
        objp = np.zeros((rows * columns, 3), np.float32)
        objp[:, :2] = np.mgrid[0:rows, 0:columns].T.reshape(-1, 2)
        objp = world_scaling * objp

        gray = cv2.cvtColor(left_frame, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, (rows, columns), None)

        cv2.drawChessboardCorners(left_frame, (rows, columns), corners, ret)

        ret, rvec, tvec = cv2.solvePnP(objp, corners, left_camera_matrix, left_camera_distortion)
        R, _ = cv2.Rodrigues(rvec)  # rvec is Rotation matrix in Rodrigues vector form

        unitv_points = 5 * np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype='float32').reshape((4, 1, 3))
        # axes colors are RGB format to indicate XYZ axes.
        colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]

        # project origin points to frame 0
        points, _ = cv2.projectPoints(unitv_points, R, tvec, left_camera_matrix, left_camera_distortion)
        points = points.reshape((4, 2)).astype(np.int32)
        origin = tuple(points[0])
        for col, _p in zip(colors, points[1:]):
            _p = tuple(_p.astype(np.int32))
            cv2.line(left_camera_matrix, origin, _p, col, 2)

        # project origin points to frame1
        R_W1 = R1 @ R
        T_W1 = R1 @ tvec + T1
        points, _ = cv2.projectPoints(unitv_points, R_W1, T_W1, right_camera_matrix, right_camera_distortion)
        points = points.reshape((4, 2)).astype(np.int32)
        origin = tuple(points[0])
        for col, _p in zip(colors, points[1:]):
            _p = tuple(_p.astype(np.int32))
            cv2.line(right_frame, origin, _p, col, 2)

        return R, tvec, R_W1, T_W1

    def delete_calibration(self, uid: str):
        self.stereo_calibration_repository.delete(uid)
