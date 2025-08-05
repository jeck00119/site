import cv2
import numpy as np

from services.algorithms.basic.dependencies.abstract_basic_algorithm import AbstractBasicAlgorithm
from services.algorithms.basic.models.data_representation import SimpleBlock, NumpyType


class OpeningAlgorithm(AbstractBasicAlgorithm):
    def __init__(self, kernel_size):
        super(OpeningAlgorithm, self).__init__()
        self.kernelSize = kernel_size

    @classmethod
    def from_dict(cls, data: dict):
        return cls(kernel_size=data["kernelSize"])

    def execute(self, block: SimpleBlock = None):
        frame = block.ins[0].value()

        out = NumpyType()
        self.operation(block.ins[0], out)
        block.outs[0].set_value(out.value())

        return block

    def operation(self, frame: NumpyType, out1: NumpyType):
        kernel = np.ones(shape=(self.kernelSize, self.kernelSize), dtype=np.uint8)
        out1.set_value(cv2.morphologyEx(frame.value(), cv2.MORPH_OPEN, kernel))
