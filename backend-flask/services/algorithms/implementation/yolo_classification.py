import copy

import cv2
import numpy as np
import torch
from ultralytics import YOLO

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi
from src.yolo_cam.eigen_cam import EigenCAM
from src.yolo_cam.utils.image import show_cam_on_image


class YoloClassificationAlgorithm(AbstractAlgorithm):
    def __init__(self, graphics, model_path='', device='0', confidence_threshold=0.7,
                 use_dnn=False, reference_algorithm=None, golden_position=None):
        super(YoloClassificationAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                          golden_position=golden_position)
        self.model = None
        self.model_path = model_path

        self.device = device
        self.confidence_threshold = confidence_threshold
        self.use_dnn = use_dnn

    @property
    def model_path(self):
        return self._model_path

    @model_path.setter
    def model_path(self, value):
        self._model_path = value
        self.load_model()

    def load_model(self):
        try:
            self.model = YOLO(f"assets/yolov8_classification/{self.model_path}")
        except FileNotFoundError:
            self.model = None
        except NotImplementedError:
            self.model = None

    def execute(self, frame: np.ndarray):

        # cv2.imshow("frame", frame)
        # cv2.waitKey(0)

        frame_copy = frame.copy()

        # frame_copy = cv2.GaussianBlur(frame_copy, (25, 25), 1.8)

        self.algorithm_result = AlgorithmResult()

        if self.device.lower() == "gpu" or self.device == "0":
            self.device = "0"
        else:
            self.device = "cpu"

        graphics_copy = copy.deepcopy(self.graphics)

        displacement = [0, 0]

        if self.reference_algorithm is not None:
            algorithm_result = self.reference_algorithm.execute(frame_copy)
            if algorithm_result.data.x is not None:
                displacement = [algorithm_result.data.x, algorithm_result.data.y]
                for roi in graphics_copy:
                    roi["bound"][0] += algorithm_result.data.x
                    roi["bound"][1] += algorithm_result.data.y

        roi, coordinates = crop_roi(frame_copy, roi_offset=graphics_copy[0]["offset"],
                                    roi_bound=graphics_copy[0]["bound"], roi_rect=graphics_copy[0]["rect"],
                                    rotation=graphics_copy[0]["rotation"])

        target_layers = [self.model.model.model[-2]]

        image_size = self.model.overrides['imgsz']

        cam_input = cv2.resize(roi, (image_size, image_size))
        rgb_img = cam_input.copy()
        cam_input = np.float32(cam_input) / 255

        # cv2.imshow('sfdsfsdfs', rgb_img)
        # cv2.waitKey(0)

        cam = EigenCAM(self.model, target_layers, task='cls')

        grayscale_cam = cam(rgb_img)[0, :, :]
        cam_image = show_cam_on_image(cam_input, grayscale_cam, use_rgb=True)

        cam_image = cv2.cvtColor(cam_image, cv2.COLOR_RGB2BGR)

        cam_image = cv2.resize(cam_image, (roi.shape[1], roi.shape[0]))

        # print()

        # plt.imshow(cam_image)
        # plt.show()

        # frame_pil = Image.fromarray(roi)

        results = self.model(rgb_img)

        classes = results[0].names

        res = classes[torch.argmax(results[0].probs.data).item()]

        org = (0, 30)

        if res == "ok":
            color = (0, 255, 0)
        else:
            color = (0, 0, 255)

        roi = cv2.putText(roi, res, org, cv2.FONT_HERSHEY_SIMPLEX,
                          1, color, 2, cv2.LINE_AA)

        self.algorithm_result.image = frame
        self.algorithm_result.imageRoi = cam_image
        self.algorithm_result.debugImages = [cam_image, roi, rgb_img]
        return self.algorithm_result
