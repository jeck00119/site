from services.algorithms.models.algorithm_parameters_model import AlgorithmParametersModel


class LineReferenceAlgorithmModel(AlgorithmParametersModel):
    rho: float = 1.00
    theta: float = 1.00
    threshold: int = 50
    min_line_length: int = 50
    max_line_gap: int = 10

    golden_position: list = [0, 0]

    def get_ui_from_type(self):
        return self.load_ui_dictionary("services/algorithms/implementation/ui_objects/line_reference.json")
