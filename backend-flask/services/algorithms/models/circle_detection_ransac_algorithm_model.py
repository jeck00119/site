from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class CircleDetectionRansacAlgorithmModel(AlgorithmParametersModel):
    median_blur_kernel: int = 0
    canny_lower_thresh: int = 0
    canny_upper_thresh: int = 0
    ransac_max_trials: int = 0

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
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/circle_detection_ransac.json")
