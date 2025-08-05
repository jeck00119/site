from services.algorithms.basic.implementation.bilateral_filter_algorithm import BilateralFilterAlgorithm
from services.algorithms.basic.implementation.binarization_algorithm import BinarizationAlgorithm
from services.algorithms.basic.implementation.box_blur_algorithm import BoxBlurAlgorithm
from services.algorithms.basic.implementation.dmc_algorithm import DmcAlgorithm
from services.algorithms.basic.implementation.double_threshold_binarization_algorithm import \
    DoubleThresholdBinarizationAlgorithm
from services.algorithms.basic.implementation.edge_detection_algorithm import EdgeDetectionAlgorithm
from services.algorithms.basic.implementation.extract_region_algorithm import ExtractRegionAlgorithm
from services.algorithms.basic.implementation.grayscale_algorithm import GrayscaleAlgorithm
from services.algorithms.basic.implementation.opening_algorithm import OpeningAlgorithm
from services.algorithms.basic.models.basic_algorithms_models import EnumBasicAlgorithmType


class BasicAlgorithmFactory(object):
    @staticmethod
    def create_algorithm(alg_type, model):
        if EnumBasicAlgorithmType.bilateral_filter == alg_type:
            return BilateralFilterAlgorithm(**model.model_dump())
        if EnumBasicAlgorithmType.binarization == alg_type:
            return BinarizationAlgorithm(**model.model_dump())
        elif EnumBasicAlgorithmType.dmc == alg_type:
            return DmcAlgorithm(**model.model_dump())
        elif EnumBasicAlgorithmType.double_threshold_binarization == alg_type:
            return DoubleThresholdBinarizationAlgorithm(**model.model_dump())
        elif EnumBasicAlgorithmType.opening == alg_type:
            return OpeningAlgorithm(**model.model_dump())
        elif EnumBasicAlgorithmType.box_blur == alg_type:
            return BoxBlurAlgorithm(**model.model_dump())
        elif EnumBasicAlgorithmType.edge_detection == alg_type:
            return EdgeDetectionAlgorithm(**model.model_dump())
        elif EnumBasicAlgorithmType.grayscale == alg_type:
            return GrayscaleAlgorithm()
        elif EnumBasicAlgorithmType.extract_region == alg_type:
            return ExtractRegionAlgorithm(**model.model_dump())
