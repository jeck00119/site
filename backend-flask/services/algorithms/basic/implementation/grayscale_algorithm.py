import cv2

from services.algorithms.basic.dependencies.abstract_basic_algorithm import AbstractBasicAlgorithm
from services.algorithms.basic.models.data_representation import SimpleBlock, NumpyType


class GrayscaleAlgorithm(AbstractBasicAlgorithm):
    def __init__(self):
        super(GrayscaleAlgorithm, self).__init__()

    @classmethod
    def from_dict(cls, data: dict):
        return cls()

    def execute(self, block: SimpleBlock = None):
        out = NumpyType()
        self.operation(block.ins[0], out)
        block.outs[0].set_value(out.value())

        return block

    def operation(self, frame: NumpyType,  out1: NumpyType):
        gray = cv2.cvtColor(frame.value(), cv2.COLOR_BGR2GRAY)
        out1.set_value(gray)
