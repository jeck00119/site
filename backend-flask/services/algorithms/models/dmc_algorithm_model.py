from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class DmcAlgorithmModel(AlgorithmParametersModel):
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
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/dmc.json")
