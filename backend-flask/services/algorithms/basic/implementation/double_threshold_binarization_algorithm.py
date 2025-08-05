import cv2
import numpy as np

from services.algorithms.basic.dependencies.abstract_basic_algorithm import AbstractBasicAlgorithm
from services.algorithms.basic.models.data_representation import SimpleBlock, NumpyType


class DoubleThresholdBinarizationAlgorithm(AbstractBasicAlgorithm):
    def __init__(self, first_threshold: int, second_threshold: int):
        super(DoubleThresholdBinarizationAlgorithm, self).__init__()
        self.firstThreshold = first_threshold
        self.secondThreshold = second_threshold

    @classmethod
    def from_dict(cls, data: dict):
        return cls(first_threshold=data["firstThreshold"], second_threshold=data["secondThreshold"])

    def execute(self, block: SimpleBlock = None):
        out = NumpyType()
        self.operation(block.ins[0], out)
        block.outs[0].set_value(out.value())

        return block

    def operation(self, frame: NumpyType, out1: NumpyType):
        frame = frame.value()
        if len(frame.shape) == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        res = ((frame >= self.firstThreshold).astype(int) * (frame <= self.secondThreshold).astype(int)) * 255
        res = res.astype(np.uint8)

        out1.set_value(res)
