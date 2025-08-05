import os.path
from os import listdir
from os.path import join, isfile

from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class SAMAlgorithmModel(AlgorithmParametersModel):
    model_path: str = ''
    file_data: list = ['', '']
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
        if not os.path.isdir("assets/sam"):
            os.mkdir("assets/sam")

        files = [f for f in listdir("assets/sam") if isfile(join("assets/sam", f))]
        ui_dict = self.load_ui_dictionary("services/algorithms/implementation/ui_objects/sam_alg.json")
        ui_dict[0]["values"] = [file.split('.')[0] for file in files] + [""]
        return ui_dict
