import cv2

from services.algorithms.basic.dependencies.abstract_basic_algorithm import AbstractBasicAlgorithm
from services.algorithms.basic.models.data_representation import SimpleBlock, NumpyType


class EdgeDetectionAlgorithm(AbstractBasicAlgorithm):
    def __init__(self, canny_first_threshold, canny_second_threshold):
        super(EdgeDetectionAlgorithm, self).__init__()
        self.canny_first_threshold = canny_first_threshold
        self.canny_second_threshold = canny_second_threshold

    @classmethod
    def from_dict(cls, data: dict):
        return cls(canny_first_threshold=data["canny_first_threshold"],
                   canny_second_threshold=data["canny_second_threshold"])

    def execute(self, block: SimpleBlock = None):
        out = NumpyType()
        self.operation(block.ins[0], out)
        block.outs[0].set_value(out.value())

        return block

    def operation(self, frame: NumpyType,  out1: NumpyType):
        edges = cv2.Canny(frame.value(), self.canny_first_threshold, self.canny_second_threshold)
        out1.set_value(edges)
