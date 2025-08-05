from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class GraphSegmentationAlgorithmModel(AlgorithmParametersModel):
    k: int = 300
    min_size: int = 100
    segmentation_type: str = "GRAYSCALE"
    blur_kernel_size: int = 1
    sigma: float = 0.00

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
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/graph_segmentation.json")
