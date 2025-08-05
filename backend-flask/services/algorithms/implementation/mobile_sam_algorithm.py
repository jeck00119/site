import cv2
import numpy as np
from ultralytics import SAM

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult


class MobileSAMAlgorithm(AbstractAlgorithm):
    def __init__(self, graphics, reference_algorithm=None, golden_position=None):
        super(MobileSAMAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                 golden_position=golden_position)

        self.model = None
        self.load_model()

    def load_model(self):
        self.model = SAM("assets/mobile_sam/mobile_sam.pt")

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        box = [
            self.graphics[0]["bound"][0],
            self.graphics[0]["bound"][1],
            self.graphics[0]["bound"][0] + self.graphics[0]["bound"][2],
            self.graphics[0]["bound"][1] + self.graphics[0]["bound"][3]
        ]

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        res = self.model.predict(frame_rgb, bboxes=box)
        mask = res[0].masks.data[0].cpu().numpy()

        self.algorithm_result.imageRoi = frame * mask[..., None]
        self.algorithm_result.data = {}
        self.algorithm_result.debugImages = [frame * mask[..., None]]

        return self.algorithm_result
