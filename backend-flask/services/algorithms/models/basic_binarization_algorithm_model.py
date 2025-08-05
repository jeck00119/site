from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class BasicBinarizationAlgorithmModel(AlgorithmParametersModel):
    binary_threshold: int = 120
    binary_inverse: bool = False
    white_ratio: float = 0.5
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

    def get_ui_from_type(self):
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/basic_binarization.json")
