from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class ClipsReferenceAlgorithmModel(AlgorithmParametersModel):
    blur_kernel_size: int = 5
    blur_sigma: float = 0.00
    adaptive_threshold_block_size: int = 121
    adaptive_threshold_constant: int = 2
    min_contour_area: int = 1500
    kernel_direction: str = "Horizontal"
    kernel_size: int = 27
    closing_kernel: int = 1

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
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/clips_reference.json")
