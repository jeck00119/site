from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class OCRAlgorithmModel(AlgorithmParametersModel):
    expected_text: str = ""

    width_resize_factor: float = 2.10
    height_resize_factor: float = 2.00

    adaptive_threshold_block_size: int = 15
    adaptive_threshold_constant: int = 10

    blur_kernel_size: int = 5

    opening_kernel_size: int = 2
    closing_kernel_size: int = 2

    trained_data_file: str = ""

    chars_to_detect: str = ""
    segmentation_mode: str = "3"
    similarity_threshold: float = 0.0

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
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/ocr.json")
