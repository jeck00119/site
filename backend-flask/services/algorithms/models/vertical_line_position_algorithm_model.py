from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class VerticalLinePositionAlgorithmModel(AlgorithmParametersModel):
    binary_threshold: int = 0
    vertical_start: int = 0
    vertical_stop: int = 0

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
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/vertical_line.json")
