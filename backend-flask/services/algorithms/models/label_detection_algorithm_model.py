from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class LabelDetectionAlgorithmModel(AlgorithmParametersModel):
    blur_kernel_size: int = 7
    bin_lower_threshold: int = 185
    bin_upper_threshold: int = 255
    canny_first_threshold: int = 30
    canny_second_threshold: int = 200
    white_region_threshold: int = 170
    board_angle_offset: int = 0
    app_type: str = "BMU EVO"

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
        },
        {
            "color": "rgba(235, 98, 52, 0.5)",
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
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/label_detection.json")
