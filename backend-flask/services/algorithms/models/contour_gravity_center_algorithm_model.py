from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class ContourGravityCenterAlgorithmModel(AlgorithmParametersModel):
    gaussian_blur_kernel_size: int = 11
    gaussian_blur_sigma: float = 0.0
    bin_low_threshold: int = 127
    closing_kernel_size: int = 5
    invert_thresholding: bool = False

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
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/contour_gravity_center.json")
