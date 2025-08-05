import copy

import cv2
import numpy as np
import supervision as sv
from ultralytics import YOLO

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class CableDetectionYolo8Algorithm(AbstractAlgorithm):
    def __init__(self, graphics, model_path='', device='0', confidence_threshold=0.7, iou_threshold=0.45,
                 max_detections=1000, use_dnn=False, reference_algorithm=None, golden_position=None):
        super().__init__(graphics, reference_algorithm=reference_algorithm, golden_position=golden_position)

        self.model = None
        self.model_path = model_path

        self.device = device
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.max_detections = max_detections
        self.use_dnn = use_dnn
        self.stride = None
        self.names = None

    @property
    def model_path(self):
        return self._model_path

    @model_path.setter
    def model_path(self, value):
        self._model_path = value
        self.load_model()

    def load_model(self):
        try:
            self.model = YOLO(f"assets/yolov8/{self._model_path}")
        except FileNotFoundError:
            self.model = None
        except NotImplementedError:
            self.model = None

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        if self.device.lower() == "gpu" or self.device == "0":
            self.device = "0"
        else:
            self.device = "cpu"

        graphics_copy = copy.deepcopy(self.graphics)

        if self.reference_algorithm is not None:
            algorithm_result = self.reference_algorithm.execute(frame)
            if algorithm_result.data is not None:
                reference = algorithm_result.referencePoint
                if reference.x is not None:
                    for roi in graphics_copy:
                        roi["roiBound"][0] += reference.x
                        roi["roiBound"][1] += reference.y

        roi, coordinates = crop_roi(frame, roi_offset=graphics_copy[0]["offset"],
                                    roi_bound=graphics_copy[0]["bound"], roi_rect=graphics_copy[0]["rect"],
                                    rotation=graphics_copy[0]["rotation"])

        detection_frame = frame.copy()

        start_x, start_y, end_x, end_y = coordinates
        cropped_image = detection_frame[start_y:end_y, start_x:end_x]

        # Get the dimensions of the cropped image
        cropped_height, cropped_width, _ = cropped_image.shape

        # Create a new frame with a black background of the same size as the original frame
        new_frame = np.zeros_like(detection_frame)

        # Position the cropped image on the new frame at the same region as in the original frame
        new_frame[start_y:end_y, start_x:end_x] = cropped_image

        # cv2.imshow("recv", new_frame)
        # cv2.waitKey(0)

        results = self.model(source=new_frame, conf=self.confidence_threshold, show=False, save=False, stream=True)

        # results = self.model(new_frame, imgsz=640, conf=self.confidence_threshold, iou=self.iou_threshold,
        #                      max_det=self.max_detections, agnostic_nms=True, show=False, save=False, stream=True,
        #                      device=self.device)

        labels = []

        for result in results:
            detections = sv.Detections.from_yolov8(result)

            box_annotator = sv.BoxAnnotator(
                thickness=2,
                text_thickness=2,
                text_scale=1
            )

            if '.engine' in self.model_path or ".onnx" in self.model_path:
                names = ['Clip', 'Head_Black', 'Head_Blue', 'Head_None', 'Head_Red']

                labels += [
                    f"{names[class_id]} {confidence:0.2f}"
                    for _, _, confidence, class_id, _
                    in detections
                ]
            else:
                labels += [
                    f"{self.model.model.names[class_id]} {confidence:0.2f}"
                    for _, _, confidence, class_id, _
                    in detections
                ]

            box_annotator.annotate(
                scene=new_frame,
                detections=detections,
                labels=labels
            )

            box_annotator.annotate(
                scene=detection_frame,
                detections=detections,
                labels=labels
            )

        # Extract the centered cropped image from the new image
        cropped_image = new_frame[start_y:end_y, start_x:end_x]

        clip_count = sum(label.count('Clip') for label in labels)
        head_none_count = sum(label.count('Head_None') for label in labels)
        head_blue_count = sum(label.count('Head_Blue') for label in labels)
        head_red_count = sum(label.count('Head_Red') for label in labels)
        head_black_count = sum(label.count('Head_Black') for label in labels)

        text = (f"{clip_count} Clips\n"
                f"{head_none_count} Head_None\n"
                f"{head_blue_count} Head_Blue\n"
                f"{head_red_count} Head_Red\n"
                f"{head_black_count} Head Black\n")

        # cv2.imshow("camera", frame)
        # cv2.waitKey(0)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_thickness = 2
        font_color = (0, 0, 0)  # Black color
        line_spacing = 10

        text_lines = text.strip().split('\n')
        text_width = 0
        text_height = len(text_lines) * (
                                cv2.getTextSize(text_lines[0], font, font_scale, font_thickness)[0][1] + line_spacing)

        frame_height, frame_width, _ = detection_frame.shape

        output_image = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
        output_image.fill(255)  # Fill with white color

        output_image[0:frame_height, 0:frame_width] = detection_frame

        text_x = 10
        text_y = 100  # Adjust the vertical position of the text here

        for line in text_lines:
            (w, h), _ = cv2.getTextSize(line, font, font_scale, font_thickness)
            text_width = max(text_width, w)

            cv2.rectangle(output_image, (text_x - 10, text_y - text_height - 10), (text_x + text_width, text_y + 5),
                          (180, 255, 255), cv2.FILLED)

        for i, line in enumerate(text_lines):
            line_y = text_y - text_height + (i + 1) * (h + line_spacing)
            cv2.putText(output_image, line, (text_x, line_y), font, font_scale, font_color, font_thickness)

        self.algorithm_result.image = frame
        self.algorithm_result.imageRoi = output_image
        self.algorithm_result.debugImages = [output_image, cropped_image]
        self.algorithm_result.data = {
                                        "clip_count": clip_count, 
                                        "head_none_count": head_none_count,
                                        "head_red_count": head_red_count,
                                        "head_blue_count": head_blue_count,
                                        "head_black_count": head_black_count
                                      }
        return self.algorithm_result
