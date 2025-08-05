import cv2

from services.algorithms.basic.dependencies.abstract_basic_algorithm import AbstractBasicAlgorithm
from services.algorithms.basic.models.data_representation import SimpleBlock, NumpyType


class BinarizationAlgorithm(AbstractBasicAlgorithm):
    def __init__(self, threshold):
        super(BinarizationAlgorithm, self).__init__()
        self.threshold = threshold

    @classmethod
    def from_dict(cls, data: dict):
        return cls(threshold=data["threshold"])

    def execute(self, block: SimpleBlock = None):
        out = NumpyType()
        self.operation(block.ins[0], out)
        block.outs[0].set_value(out.value())

        return block

    def operation(self, frame: NumpyType,  out1: NumpyType):
        out1.set_value(cv2.threshold(frame.value(), self.threshold, 255, cv2.THRESH_BINARY)[1])
