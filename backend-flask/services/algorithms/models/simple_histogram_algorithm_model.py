from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class SimpleHistogramAlgorithmModel(AlgorithmParametersModel):
    graphics: list = [
        {
            "color": "rgba(140, 235, 52, 0.5)",
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
            ],
            "masks": [],
            "masksColors": []
        }
    ]
    golden_position: list = [0, 0]
