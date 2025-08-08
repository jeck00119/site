import copy
import random
import time

import cv2
import numpy as np
import supervision as sv
import torch
from patched_yolo_infer import MakeCropsDetectThem, CombineDetections
from ultralytics import YOLO

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from services.algorithms.implementation.dependencies.detection_calculations import Point
from src.utils import crop_roi


class YoloAlgorithm(AbstractAlgorithm):
    def __init__(self, graphics, model_path='', device='0', confidence_threshold=0.7, iou_threshold=0.45,
                 max_detections=1000,
                 use_dnn=False, patch_inference=False, patch_size=640, patch_overlap=50,
                 reference_algorithm=None, golden_position=None):
        super(YoloAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                            golden_position=golden_position)
        self.model = None
        self.model_path = model_path

        self.device = device
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.max_detections = max_detections
        self.use_dnn = use_dnn
        self.patch_inference = patch_inference
        self.patch_size = patch_size
        self.patch_overlap = patch_overlap

    @property
    def model_path(self):
        return self._model_path

    @model_path.setter
    def model_path(self, value):
        self._model_path = value
        self.load_model()

    def load_model(self):
        try:
            self.model = YOLO(f"assets/yolov8/{self.model_path}")
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
            if hasattr(algorithm_result.data, 'x') and algorithm_result.data.x is not None:
                displacement = [algorithm_result.data.x, algorithm_result.data.y]
                for roi in graphics_copy:
                    roi["bound"][0] += algorithm_result.data.x
                    roi["bound"][1] += algorithm_result.data.y

        # Check if graphics_copy has at least one element before accessing
        if len(graphics_copy) == 0:
            # Use full frame if no graphics defined
            roi = frame_copy
            coordinates = (0, 0, frame_copy.shape[1], frame_copy.shape[0])
        else:
            roi, coordinates = crop_roi(frame_copy, roi_offset=graphics_copy[0]["offset"],
                                        roi_bound=graphics_copy[0]["bound"], roi_rect=graphics_copy[0]["rect"],
                                        rotation=graphics_copy[0]["rotation"])

        # timestamp = str(time.time()).split('.')[0]
        # filename = timestamp + '.png'
        # cv2.imwrite(filename, roi)

        detection_frame = frame_copy.copy()

        start_x, start_y, end_x, end_y = coordinates
        cropped_image = detection_frame[start_y:end_y, start_x:end_x]

        # Apply masks only if graphics are defined
        if len(graphics_copy) > 0:
            for i, mask in enumerate(graphics_copy[0]["masks"]):
                masked = self.mask_region(cropped_image, mask,
                                          color=(
                                              graphics_copy[0]["masksColors"][i][2], graphics_copy[0]["masksColors"][i][1],
                                              graphics_copy[0]["masksColors"][i][0]))
                cropped_image = masked

        # Get the dimensions of the cropped image
        cropped_height, cropped_width, _ = cropped_image.shape

        # Create a new frame with a black background of the same size as the original frame
        new_frame = np.zeros_like(detection_frame)

        # Position the cropped image on the new frame at the same region as in the original frame
        new_frame[start_y:end_y, start_x:end_x] = cropped_image

        # cv2.imshow("recv", new_frame)
        # cv2.waitKey(0)

        # results = self.model(source=frame, conf=self.confidenceThreshold, show=False, save=False, stream=True)

        # results = self.model(new_frame, imgsz=640, conf=self.confidence_threshold, iou=self.iou_threshold,
        #                      max_det=self.max_detections, agnostic_nms=True, show=False, save=False, stream=True,
        #                      device=self.device)

        # new_frame = roi.copy()
        #
        # new_frame = cv2.resize(new_frame, (frame.shape[1], frame.shape[0]))

        boxes = None
        masks = None
        obb = None

        classes = None

        if self.patch_inference:
            element_crops = MakeCropsDetectThem(
                image=new_frame,
                model_path=f"assets/yolov8/{self.model_path}",
                segment=True if self.model.task == "segment" else False,
                shape_x=self.patch_size,
                shape_y=self.patch_size,
                overlap_x=self.patch_overlap,
                overlap_y=self.patch_overlap,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
            )
            result = CombineDetections(element_crops, nms_threshold=0.25)

            detections = sv.Detections(xyxy=np.array(result.filtered_boxes) if result.filtered_boxes else np.zeros(shape=(0, 4)),
                                       confidence=np.array(result.filtered_confidences) if result.filtered_confidences else np.zeros(shape=(0,)),
                                       class_id=np.array(result.filtered_classes_id) if result.filtered_classes_id else np.zeros(
                                           shape=(0,)),
                                       mask=None,
                                       )

            box_annotator = sv.BoxAnnotator(
                thickness=1
            )

            labels = [
                f"{result.class_names[class_id]} {confidence:0.2f}"
                for _, _, confidence, class_id, _
                in detections
            ]

            box_annotator.annotate(
                scene=detection_frame,
                detections=detections,
                labels=labels,
                skip_label=True
            )

            boxes = np.array(result.filtered_boxes) if len(result.filtered_boxes) != 0 else None
            classes = torch.tensor(result.filtered_classes_id) if len(result.filtered_classes_id) != 0 else None
            masks = np.array(result.filtered_masks) if len(result.filtered_masks) != 0 else None

            found_objects = {}

            if boxes is not None:
                for box, cl in zip(boxes, classes):
                    found_objects[result.class_names[int(cl)]] = box.tolist()
        else:
            results = self.model.predict(new_frame, imgsz=640, conf=self.confidence_threshold, iou=self.iou_threshold,
                                         max_det=self.max_detections, agnostic_nms=True, show=False, save=False,
                                         stream=True,
                                         device=self.device)

            labels = []

            for result in results:
                detections = sv.Detections.from_ultralytics(result)

                if self.model.task == "segment":
                    if result.masks:
                        masks = result.masks.xy
                elif self.model.task == "obb":
                    obb = result.obb.xyxy

                classes = result.boxes.cls.cpu().numpy().astype(int)
                boxes = detections.xyxy

                box_annotator = sv.BoxAnnotator(
                    thickness=1
                )

                labels += [
                    f"{self.model.model.names[class_id]} {confidence:0.2f}"
                    for _, _, confidence, class_id, _
                    in detections
                ]

                # box_annotator.annotate(
                #     scene=new_frame,
                #     detections=detections,
                #     labels=labels
                # )

                # box_annotator.annotate(
                #     scene=detection_frame,
                #     detections=detections,
                #     labels=labels,
                #     skip_label=True
                # )

            found_objects = {}

            for box, cl in zip(boxes, classes):
                found_objects[self.model.model.names[cl]] = box.tolist()

        timestamp = ''.join(str(time.time()).split('.'))
        filename = timestamp + '_masked.png'
        cv2.imwrite(filename, cropped_image)

        frame_seg = frame.copy()

        ref_points_x = []
        ref_points_y = []

        if boxes is not None:
            sorted_indices = boxes[:, 0].argsort()
            sorted_boxes = boxes[sorted_indices]

            # if sorted_boxes.shape[0] != 0:
            #     ref_point_x = sorted_boxes[0][0]
            #     ref_point_y = sorted_boxes[0][1]

            for i in range(sorted_boxes.shape[0]):
                # frame = cv2.rectangle(frame, (int(sorted_boxes[i][0]), int(sorted_boxes[i][1])),
                #                       (int(sorted_boxes[i][2]), int(sorted_boxes[i][3])), (0, 255, 0), -1)
                print(sorted_boxes[i][0] - displacement[0])
                print(sorted_boxes[i][1] - displacement[1])
                print(sorted_boxes[i][2] - displacement[0])
                print(sorted_boxes[i][3] - displacement[1])
                print()

                ref_points_x.append(sorted_boxes[i][0])
                ref_points_y.append(sorted_boxes[i][1])
        seg_result = np.zeros(shape=frame.shape, dtype=np.uint8)

        color = (0, 255, 0)
        alpha = 0.5

        masks_drawn = False

        # seg_result = None

        yolo_classes = list(self.model.names.values())
        classes_ids = [yolo_classes.index(clas) for clas in yolo_classes]

        colors = [random.choices(range(256), k=3) for _ in classes_ids]

        if masks is not None:
            for mask, c in zip(masks, classes):
                color = color[::-1]
                points = np.int32([mask])

                color_number = classes_ids.index(int(c))

                if not masks_drawn:
                    seg_result = cv2.fillPoly(frame_seg, points, colors[color_number])
                    masks_drawn = True
                else:
                    seg_result = cv2.fillPoly(seg_result, points, colors[color_number])

                # colored_mask = np.expand_dims(mask, 0).repeat(3, axis=0)
                # colored_mask = np.moveaxis(colored_mask, 0, -1)
                # masked = np.ma.MaskedArray(frame_seg, mask=colored_mask, fill_value=color)
                # image_overlay = masked.filled()
                # if seg_result is None:
                #     seg_result = cv2.addWeighted(frame_seg, 1 - alpha, image_overlay, alpha, 0)
                # else:
                #     seg_result = cv2.addWeighted(seg_result, 1 - alpha, image_overlay, alpha, 0)

        # Extract the centered cropped image from the new image
        cropped_image = new_frame[start_y:end_y, start_x:end_x]

        points = []

        if len(ref_points_x) != 0:
            for i in range(len(ref_points_x)):
                point = Point(float(ref_points_x[i]), float(ref_points_y[i]))
                points.append(point)
        # else:
        #     raise ReferenceNotFound

        self.algorithm_result.referencePoints = points

        if len(points) != 0:
            self.algorithm_result.referenceData = self.compute_displacement(points[self.reference_point_idx])
        else:
            self.algorithm_result.referenceData = [-1, -1]

        self.algorithm_result.data = found_objects
        self.algorithm_result.image = frame
        self.algorithm_result.imageRoi = detection_frame
        self.algorithm_result.debugImages = [detection_frame, cropped_image, roi, seg_result]
        return self.algorithm_result
