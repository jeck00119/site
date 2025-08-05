from services.algorithms.algorithms_models import EnumReferenceAlgorithmType
from services.algorithms.implementation.circle_detection_ransac_algorithm import CircleDetectionRansacAlgorithm
from services.algorithms.implementation.clips_reference_algorithm import ClipsReferenceAlgorithm
from services.algorithms.implementation.contour_gravity_center_algorithm import ContourGravityCenterAlgorithm
from services.algorithms.implementation.horizontal_line_position_algorithm import HorizontalLinePositionAlgorithm
from services.algorithms.implementation.line_reference_algorithm import LineReferenceAlgorithm
from services.algorithms.implementation.rtdetr_algorithm import RTDETRAlgorithm
from services.algorithms.implementation.template_detection_algorithm import TemplateDetectionAlgorithm
from services.algorithms.implementation.vertical_line_position_algorithm import VerticalLinePositionAlgorithm
from services.algorithms.implementation.yolo_algorithm import YoloAlgorithm


class ReferenceAlgorithmFactory(object):
    def __init__(self):
        pass

    @staticmethod
    def create_algorithm(algorithm_type, model):
        if algorithm_type == EnumReferenceAlgorithmType.contour_gravity_center:
            return ContourGravityCenterAlgorithm(**model)
        elif algorithm_type == EnumReferenceAlgorithmType.circle_detection_ransac:
            return CircleDetectionRansacAlgorithm(**model)
        elif algorithm_type == EnumReferenceAlgorithmType.template_detection:
            return TemplateDetectionAlgorithm(**model)
        elif algorithm_type == EnumReferenceAlgorithmType.line_reference:
            return LineReferenceAlgorithm(**model)
        elif algorithm_type == EnumReferenceAlgorithmType.vertical_line:
            return VerticalLinePositionAlgorithm(**model)
        elif algorithm_type == EnumReferenceAlgorithmType.horizontal_line:
            return HorizontalLinePositionAlgorithm(**model)
        elif algorithm_type == EnumReferenceAlgorithmType.clips_reference:
            return ClipsReferenceAlgorithm(**model)
        elif algorithm_type == EnumReferenceAlgorithmType.yolo:
            return YoloAlgorithm(**model)
        elif algorithm_type == EnumReferenceAlgorithmType.rtdetr:
            return RTDETRAlgorithm(**model)
