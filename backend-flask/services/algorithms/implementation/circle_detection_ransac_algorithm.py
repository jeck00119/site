import cv2
import numpy as np
from skimage import measure, draw

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from services.algorithms.implementation.dependencies.detection_calculations import Point
from src.utils import crop_roi


class CircleDetectionRansacAlgorithm(AbstractAlgorithm):
    def __init__(self, median_blur_kernel, canny_lower_thresh, canny_upper_thresh, ransac_max_trials, graphics,
                 reference_algorithm=None, golden_position=None):
        super(CircleDetectionRansacAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                             golden_position=golden_position)
        self.median_blur_kernel = median_blur_kernel
        self.canny_lower_thresh = canny_lower_thresh
        self.canny_upper_thresh = canny_upper_thresh
        self.ransac_max_trials = ransac_max_trials

    def execute(self, frame):
        self.algorithm_result = AlgorithmResult()

        cv2.imwrite("circle_frame.png", frame)

        frame, _ = crop_roi(frame, self.graphics[0]["offset"], self.graphics[0]["bound"],
                            self.graphics[0]["rect"], self.graphics[0]["rotation"])

        # img_blurred = cv2.fastNlMeansDenoisingColored(frame.copy(), None, 30, 60, 7, 21)

        # img_blurred = cv2.bilateralFilter(frame.copy(),20, 100, 80)

        # img_blurred = cv2.filter2D(frame.copy(), -1, kernel)

        # img_blurred = cv2.GaussianBlur(frame.copy(), (5, 5), 0)

        img_blurred = cv2.medianBlur(frame, self.median_blur_kernel)

        img_gray = cv2.cvtColor(img_blurred, cv2.COLOR_BGR2GRAY)

        canny = cv2.Canny(img_gray, self.canny_lower_thresh, self.canny_upper_thresh)

        coords = np.column_stack(np.nonzero(canny))

        try:
            model, inliers = measure.ransac(data=coords, model_class=measure.CircleModel,
                                            min_samples=3, residual_threshold=1,
                                            max_trials=self.ransac_max_trials)

            rr, cc = draw.circle_perimeter(int(model.params[0]), int(model.params[1]), int(model.params[2]),
                                           shape=frame.shape)

            frame[rr, cc] = 1

            # center_coord_x = np.uint16(np.around(model.params[1]))
            # center_coord_y = np.uint16(np.around(model.params[0]))
            # radius = np.uint16(np.around(model.params[2]))

            center_coord_x = int(model.params[1])
            center_coord_y = int(model.params[0])
            radius = int(model.params[2])

            cv2.circle(frame, (center_coord_x, center_coord_y), radius, (255, 0, 0), 4)
            cv2.circle(frame, (center_coord_x, center_coord_y), 1, (0, 255, 0), 1)

            middle_point = Point(center_coord_x, center_coord_y)
        except:
            middle_point = Point(123, 123)

        self.algorithm_result.referencePoints = [middle_point]
        self.algorithm_result.data = self.compute_displacement(middle_point)
        self.algorithm_result.imageRoi = frame
        self.algorithm_result.debugImages = [canny, frame]

        return self.algorithm_result
