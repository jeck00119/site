from os import listdir, mkdir
from os.path import join, isfile, isdir

from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class CableDetectionYoloV8AlgorithmModel(AlgorithmParametersModel):
    model_path: str = ''
    device: str = 'CPU'
    confidence_threshold: float = 0.7
    iou_threshold: float = 0.45
    max_detections: int = 1000
    use_dnn: bool = False

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
        if not isdir("assets/yolov8"):
            mkdir("assets/yolov8")

        files = [f for f in listdir("assets/yolov8") if isfile(join("assets/yolov8", f))]
        ui_dict = self.load_ui_dictionary("services/algorithms/implementation/ui_objects/cable_detection_yolov8.json")
        ui_dict[0]["values"] = [""] + files
        return ui_dict
