import cv2
import numpy as np
import supervision as sv
import torch
from segment_anything import sam_model_registry, SamPredictor

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult


class SAMAlgorithm(AbstractAlgorithm):
    def __init__(self, model_path, file_data, graphics, reference_algorithm=None, golden_position=None):
        super(SAMAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                           golden_position=golden_position)

        self._model_path = model_path
        self.sam_model = None
        self.mask_predictor = None

    @property
    def model_path(self):
        return self._model_path

    @model_path.setter
    def model_path(self, value):
        self._model_path = value
        self.load_model()

    def load_model(self):
        if self._model_path != '':
            checkpoint = f"assets/sam/{self._model_path}.pth"

            model_type = "vit_b"
            if "vit_b" in self._model_path:
                model_type = "vit_b"

            if "vit_l" in self._model_path:
                model_type = "vit_l"

            if "vit_h" in self._model_path:
                model_type = "vit_h"

            self.sam_model = sam_model_registry[model_type](checkpoint=checkpoint).to(
                device=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'))
            self.mask_predictor = SamPredictor(self.sam_model)

    def execute(self, frame):
        self.algorithm_result = AlgorithmResult()

        box = np.array([
            self.graphics[0]["bound"][0],
            self.graphics[0]["bound"][1],
            self.graphics[0]["bound"][0] + self.graphics[0]["bound"][2],
            self.graphics[0]["bound"][1] + self.graphics[0]["bound"][3]
        ])

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.mask_predictor.set_image(frame_rgb)

        masks, scores, logits = self.mask_predictor.predict(
            box=box,
            multimask_output=True
        )

        mask_annotator = sv.MaskAnnotator()

        detections = sv.Detections(xyxy=sv.mask_to_xyxy(masks=masks), mask=masks)

        annotated_image = mask_annotator.annotate(scene=frame.copy(), detections=detections)

        mask = detections.mask[np.argmax(scores)].astype(np.uint8)
        mask = mask * 255

        self.algorithm_result.imageRoi = frame * detections.mask[np.argmax(scores)][..., None]
        self.algorithm_result.data = {}
        self.algorithm_result.debugImages = [frame * detections.mask[np.argmax(scores)][..., None]]

        return self.algorithm_result
