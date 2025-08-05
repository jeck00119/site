from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class CableInspectionAlgorithmModel(AlgorithmParametersModel):
    blur_kernel_size: int = 19
    bin_lower_threshold: int = 185
    bin_upper_threshold: int = 255
    canny_first_threshold: int = 30
    canny_second_threshold: int = 200
    flatten_contour_step: int = 50
    threshold_angle: int = 10
    contour_variation_epsilon: int = 10
    reference_distance: int = 1
    absolute_distance: bool = True

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
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/cable_inspection.json")
