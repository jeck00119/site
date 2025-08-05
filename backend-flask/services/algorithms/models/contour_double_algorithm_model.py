from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class ContourDoubleAlgorithmModel(AlgorithmParametersModel):
    white_threshold: int = 0
    black_threshold: int = 0

    gamma: float = 0.01

    erode_kernel: int = 0
    erode_iterations: int = 0

    dilate_kernel: int = 0
    dilate_iterations: int = 0

    blur_kernel: int = 0

    part_area_min: int = 0
    part_area_max: int = 0

    enable_inv_binarization: bool = False

    enable_adaptive_threshold: bool = False
    adaptive_offset: int = 0
    enable_histogram_debug: bool = False

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
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/contour_double.json")
