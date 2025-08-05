import cv2

from services.algorithms.basic.dependencies.abstract_basic_algorithm import AbstractBasicAlgorithm
from services.algorithms.basic.models.data_representation import SimpleBlock, NumpyType


class BilateralFilterAlgorithm(AbstractBasicAlgorithm):
    borderTypes = {
        "REPLICATE": cv2.BORDER_REPLICATE,
        "REFLECT": cv2.BORDER_REFLECT,
        "WRAP": cv2.BORDER_WRAP,
        "DEFAULT": cv2.BORDER_REFLECT_101,
        "TRANSPARENT": cv2.BORDER_TRANSPARENT
    }

    def __init__(self, diameter, sigma_color, sigma_space, border_type):
        super(BilateralFilterAlgorithm, self).__init__()
        self.diameter = diameter
        self.sigma_color = sigma_color
        self.sigma_space = sigma_space
        self.border_type = border_type

    @classmethod
    def from_dict(cls, data: dict):
        return cls(diameter=data["diameter"], sigma_color=data["sigmaColor"], sigma_space=data["sigmaSpace"],
                   border_type=data["borderType"])

    def execute(self, block: SimpleBlock = None):
        out = NumpyType()
        self.operation(block.ins[0], out)
        block.outs[0].set_value(out.value())

        return block

    def operation(self, frame: NumpyType, out1: NumpyType):
        res = cv2.bilateralFilter(frame.value(), self.diameter, self.sigma_color, self.sigma_space,
                                  self.borderTypes[self.border_type])
        out1.set_value(res)
