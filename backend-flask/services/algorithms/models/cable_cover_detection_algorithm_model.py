from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class CableCoverDetectionAlgorithmModel(AlgorithmParametersModel):
    median_blur: int = 0
    bin_thresh: int = 0
    kernel_opening: int = 0
    kernel_closing: int = 0
    iteration_opening: int = 0
    iteration_closing: int = 0
    no_cover_area_thresh: int = 0
    black_silicone_cover_ext_x_min_dist: int = 0
    blue_cover_ext_x_min_dist: int = 0
    expected_result: str = "No Cover"

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
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/cable_cover.json")
