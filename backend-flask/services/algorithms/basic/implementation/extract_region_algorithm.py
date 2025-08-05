from services.algorithms.basic.dependencies.abstract_basic_algorithm import AbstractBasicAlgorithm
from services.algorithms.basic.models.data_representation import SimpleBlock, NumpyType
from src.utils import crop_roi


class ExtractRegionAlgorithm(AbstractBasicAlgorithm):
    def __init__(self, graphics):
        super(ExtractRegionAlgorithm, self).__init__()
        self.graphics = graphics

    @classmethod
    def from_dict(cls, data: dict):
        return cls(graphics=data["graphics"])

    def execute(self, block: SimpleBlock = None):
        out = NumpyType()
        self.operation(block.ins[0], out)
        block.outs[0].set_value(out.value())

        return block

    def operation(self, frame: NumpyType, out1: NumpyType):
        roi, _ = crop_roi(frame.value(), self.graphics[0]["offset"], self.graphics[0]["bound"],
                          self.graphics[0]["rect"], self.graphics[0]["rotation"])
        out1.set_value(roi)
