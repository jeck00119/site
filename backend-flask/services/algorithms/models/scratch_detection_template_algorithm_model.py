from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class ScratchDetectionTemplateAlgorithmModel(AlgorithmParametersModel):
    mode: str = "Reference"
    width_downsize_factor: int = 1
    height_downsize_factor: int = 1
    alpha: float = 2.00
    beta: float = 0.00
    image_denoising_strength: int = 31
    template_window_size: int = 7
    search_window_size: int = 21
    first_blur_kernel: int = 3
    sobel_kernel: int = 3
    second_blur_kernel: int = 3
    threshold: int = 49
    closing_kernel: int = 1
    opening_kernel: int = 1
    min_obj_area: int = 170
    hough_threshold: int = 62
    min_line_length: int = 10
    max_gap: int = 10
    dilation_kernel: int = 1
    adaptive_threshold_block_size: int = 3
    adaptive_threshold_constant: int = 1
    gaussian_kernel: int = 1
    gaussian_sigma: float = 0.00
    template_save_location: str = ""
    template_load_location: str = ""

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
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/scratch_template.json")
