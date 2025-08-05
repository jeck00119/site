import cv2
from pylibdmtx import pylibdmtx

from services.algorithms.basic.dependencies.abstract_basic_algorithm import AbstractBasicAlgorithm
from services.algorithms.basic.models.data_representation import SimpleBlock, NumpyType


class DmcAlgorithm(AbstractBasicAlgorithm):
    HELP = "This algorithm uses a photo and decodes a dmc"

    def __init__(self, threshold=0, gap_size=0, deviation=0, char_number=0, shrink=1, shape=0, max_count=0,
                 min_edge=0, max_edge=0, corrections=0, timeout=0):
        super(DmcAlgorithm, self).__init__()
        self.charNumber = char_number
        self.threshold = threshold
        self.gapSize = gap_size
        self.shrink = shrink
        self.deviation = deviation
        self.shape = shape
        self.corrections = corrections
        self.maxCount = max_count
        self.timeout = timeout
        self.minEdge = min_edge
        self.maxEdge = max_edge

    @classmethod
    def from_dict(cls, data: dict):
        return cls(char_number=data["charNumber"], threshold=data["threshold"], gap_size=data["gapSize"],
                   deviation=data["deviation"], shrink=data["shrink"], shape=data["shape"],
                   max_count=data["maxCount"], timeout=data["timeout"], min_edge=data["minEdge"],
                   max_edge=data["maxEdge"], corrections=data["corrections"])

    def execute(self, block: SimpleBlock = None):
        out = NumpyType()
        self.operation(block.ins[0], out)
        block.outs[0].set_value(out.value())

        return block

    def operation(self, frame: NumpyType, out1: NumpyType):
        frame = frame.value()
        frame_copy = frame.copy()

        text = None
        timeout = self.timeout if self.timeout > 0 else None
        threshold = self.threshold if self.threshold > 0 else None
        gap_size = self.gapSize if self.gapSize > 0 else None
        shape = self.shape if self.shape > 0 else None
        deviation = self.deviation if self.deviation > 0 else None
        corrections = self.corrections if self.corrections > 0 else None
        min_edge = self.minEdge if self.minEdge > 0 else None
        max_edge = self.maxEdge if self.maxEdge > 0 else None
        max_count = self.maxCount if self.maxCount > 0 else None

        barcode = pylibdmtx.decode(frame, timeout=500, shrink=self.shrink, threshold=threshold,
                                   gap_size=gap_size, shape=shape, deviation=deviation, corrections=corrections,
                                   max_edge=max_edge, min_edge=min_edge, max_count=max_count)
        barcode_data = ''
        if barcode:
            barcode_data = barcode[0].data.decode("utf-8")
            cv2.rectangle(frame_copy, (barcode[0].rect.left, barcode[0].rect.top),
                          (barcode[0].rect.left + barcode[0].rect.width, barcode[0].rect.top + barcode[0].rect.height),
                          (0, 255, 0), 4)
            if self.charNumber != 0:
                if len(barcode_data) != self.charNumber:
                    text = "Error DMC not at char len"
            if barcode_data:
                try:
                    int(barcode_data)
                    cv2.putText(frame_copy, f'{barcode_data}',
                                (barcode[0].rect.left + barcode[0].rect.width, barcode[0].rect.top + 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                (255, 0, 0), 2, cv2.LINE_AA)

                except ValueError:
                    text = ''
        else:
            text = 'None'

        out1.set_value(frame_copy)
