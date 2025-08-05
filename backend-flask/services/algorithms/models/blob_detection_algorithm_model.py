from pydantic import field_validator

from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class BlobDetectionAlgorithmModel(AlgorithmParametersModel):
    threshold_binarization: int = 0
    opening: int = 0
    closing: int = 0
    ph1: int = 0
    ph2: int = 1
    area_enable: bool = False
    circle_enable: bool = False
    conv_enable: bool = False
    inert_enable: bool = False
    area_value: int = 0
    circle_value: int = 0
    conv_value: int = 0
    inert_value: int = 0
    result_number: int = 3
    result_names: str = 'c1p1, c2p2, c3p3'

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
    golden_position: tuple = [0, 0]

    @field_validator('result_names')
    @classmethod
    def split_string(cls, v, values):
        if len(v.split(',')) == values['result_number']:
            return v.split()
        else:
            raise