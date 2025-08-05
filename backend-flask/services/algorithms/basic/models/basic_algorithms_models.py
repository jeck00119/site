from enum import Enum

from pydantic import field_validator

from src.utils import generate_uid, CamelModel


class EnumBasicAlgorithmType(str, Enum):
    bilateral_filter = "Bilateral Filter"
    binarization = "Binarization"
    dmc = "DMC"
    double_threshold_binarization = "Double Threshold Binarization"
    opening = "Opening"
    box_blur = "Box Blur"
    edge_detection = "Edge Detection"
    grayscale = "Grayscale"
    extract_region = "Extract Region"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class BilateralFilterAlgorithmModel(CamelModel):
    diameter: int = 1
    sigma_color: int = 1
    sigma_space: int = 1
    border_type: str = "DEFAULT"


class BinarizationAlgorithmModel(CamelModel):
    threshold: int = 0


class DmcAlgorithmModel(CamelModel):
    threshold: int = 0
    gap_size: int = 0
    deviation: int = 0
    char_number: int = 0
    shrink: int = 1
    shape: int = 0
    max_count: int = 0
    min_edge: int = 0
    max_edge: int = 0
    corrections: int = 0
    timeout: int = 0


class DoubleThresholdBinarizationAlgorithmModel(CamelModel):
    first_threshold: int = 0
    second_threshold: int = 0


class OpeningAlgorithmModel(CamelModel):
    kernel_size: int = 1


class BoxBlurAlgorithmModel(CamelModel):
    kernel_size: int = 1


class EdgeDetectionAlgorithmModel(CamelModel):
    canny_first_threshold: int = 30
    canny_second_threshold: int = 200


class GrayscaleAlgorithmModel(CamelModel):
    pass


class ExtractRegionAlgorithmModel(CamelModel):
    graphics: list = [
        {
            "rotation": 0,
            "bound": [
                10,
                10,
                100,
                100
            ],
            "offset": [
                0,
                0
            ],
            "rect": [
                10,
                10,
                100,
                100
            ]
        }
    ]


class BasicAlgorithmModel(CamelModel):
    uid: str = generate_uid(length=8)
    type: EnumBasicAlgorithmType
    name: str = f'Algorithm_{uid}'
    parameters: dict

    @field_validator('parameters')
    @classmethod
    def match_parameters(cls, v, values):
        if values['type'] == EnumBasicAlgorithmType.bilateral_filter:
            return BilateralFilterAlgorithmModel(**v)
        if values['type'] == EnumBasicAlgorithmType.binarization:
            return BinarizationAlgorithmModel(**v)
        if values['type'] == EnumBasicAlgorithmType.dmc:
            return DmcAlgorithmModel(**v)
        if values['type'] == EnumBasicAlgorithmType.double_threshold_binarization:
            return DoubleThresholdBinarizationAlgorithmModel(**v)
        if values['type'] == EnumBasicAlgorithmType.opening:
            return OpeningAlgorithmModel(**v)
        if values['type'] == EnumBasicAlgorithmType.box_blur:
            return BoxBlurAlgorithmModel(**v)
        if values['type'] == EnumBasicAlgorithmType.edge_detection:
            return EdgeDetectionAlgorithmModel(**v)
        if values['type'] == EnumBasicAlgorithmType.grayscale:
            return GrayscaleAlgorithmModel()
        if values['type'] == EnumBasicAlgorithmType.extract_region:
            return ExtractRegionAlgorithmModel(**v)
