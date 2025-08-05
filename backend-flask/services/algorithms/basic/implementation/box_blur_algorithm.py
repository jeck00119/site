import cv2

from services.algorithms.basic.dependencies.abstract_basic_algorithm import AbstractBasicAlgorithm
from services.algorithms.basic.models.data_representation import SimpleBlock, NumpyType


class BoxBlurAlgorithm(AbstractBasicAlgorithm):
    def __init__(self, kernel_size):
        super(BoxBlurAlgorithm, self).__init__()
        self.kernel_size = kernel_size

    @classmethod
    def from_dict(cls, data: dict):
        return cls(kernel_size=data["kernel_size"])

    def execute(self, block: SimpleBlock = None):
        out = NumpyType()
        self.operation(block.ins[0], out)
        block.outs[0].set_value(out.value())

        return block

    def operation(self, frame: NumpyType,  out1: NumpyType):
        blur = cv2.blur(frame.value(), (self.kernel_size, self.kernel_size))
        out1.set_value(blur)
