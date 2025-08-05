from services.algorithms.algorithms_models import EnumAlgorithmType
from services.algorithms.implementation.aruco_detector_algorithm import ArucoDetectorAlgorithm
from services.algorithms.implementation.barcode_scan_algorithm import BarcodeScanAlgorithm
from services.algorithms.implementation.basic_binarization_algorithm import BasicBinarizationAlgorithm
from services.algorithms.implementation.blob_detection import BlobDetection
from services.algorithms.implementation.brightness_averaging_algorithm import BrightnessAveragingAlgorithm
from services.algorithms.implementation.cable_cover_detection_algorithm import CableCoverDetectionAlgorithm
from services.algorithms.implementation.cable_detection_yolov8_algorithm import CableDetectionYolo8Algorithm
from services.algorithms.implementation.cable_inspection_algorithm import CableInspectionAlgorithm
from services.algorithms.implementation.clips_shut_algorithm import ClipsShutAlgorithm
from services.algorithms.implementation.color_averaging_algorithm import ColorAveragingAlgorithm
from services.algorithms.implementation.color_matcher_algorithm import ColorMatcherAlgorithm
from services.algorithms.implementation.conformal_hsv_algorithm import ConformalHSVAlgorithm
from services.algorithms.implementation.contour_double_algorithm import ContourDoubleAlgorithm
from services.algorithms.implementation.contour_double_hsv_algorithm import ContourDoubleHSVAlgorithm
from services.algorithms.implementation.contour_gravity_center_algorithm import ContourGravityCenterAlgorithm
from services.algorithms.implementation.contour_logic_algorithm import ContourLogicAlgorithm
from services.algorithms.implementation.dmc_algorithm import DmcDetectionAlgorithm
from services.algorithms.implementation.easy_ocr_algorithm import EasyOCRAlgorithm
from services.algorithms.implementation.foreground_subtraction_algorithm import ForegroundSubtractionAlgorithm
from services.algorithms.implementation.graph_segmentation_algorithm import GraphSegmentationAlgorithm
from services.algorithms.implementation.label_detection_algorithm import LabelDetectionAlgorithm
from services.algorithms.implementation.mobile_sam_algorithm import MobileSAMAlgorithm
from services.algorithms.implementation.motion_detection_hist_algorithm import MotionDetectionHistAlgorithm
from services.algorithms.implementation.ocr_algorithm import OCRAlgorithm
from services.algorithms.implementation.rtdetr_algorithm import RTDETRAlgorithm
from services.algorithms.implementation.sam_algorithm import SAMAlgorithm
from services.algorithms.implementation.scratch_detection_template_algorithm import ScratchDetectionTemplateAlgorithm
from services.algorithms.implementation.simple_histogram import SimpleHistogramAlgorithm
from services.algorithms.implementation.steep_detection_algorithm import SteepDetectionAlgorithm
from services.algorithms.implementation.yolo_algorithm import YoloAlgorithm
from services.algorithms.implementation.yolo_classification import YoloClassificationAlgorithm


class AlgorithmFactory(object):
    def __init__(self):
        pass

    @staticmethod
    def create_algorithm(algorithm_type, model):
        if algorithm_type == EnumAlgorithmType.basic_binarization:
            return BasicBinarizationAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.blob:
            return BlobDetection(**model)
        elif algorithm_type == EnumAlgorithmType.dmc:
            return DmcDetectionAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.simple_histogram:
            return SimpleHistogramAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.motion_detection_hist:
            return MotionDetectionHistAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.color_averaging:
            return ColorAveragingAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.brightness_averaging:
            return BrightnessAveragingAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.conformal_hsv:
            return ConformalHSVAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.contour_logic:
            return ContourLogicAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.barcode_scan:
            return BarcodeScanAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.steep_detection:
            return SteepDetectionAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.ocr:
            return OCRAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.contour_double:
            return ContourDoubleAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.contour_double_hsv:
            return ContourDoubleHSVAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.aruco_detector:
            return ArucoDetectorAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.color_matcher:
            return ColorMatcherAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.clips_shut:
            return ClipsShutAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.foreground_subtraction:
            return ForegroundSubtractionAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.graph_segmentation:
            return GraphSegmentationAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.label:
            return LabelDetectionAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.cable_inspection:
            return CableInspectionAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.cable_cover:
            return CableCoverDetectionAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.contour_gravity_center:
            return ContourGravityCenterAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.scratch_template:
            return ScratchDetectionTemplateAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.sam:
            return SAMAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.cable_detection_yolov8:
            return CableDetectionYolo8Algorithm(**model)
        elif algorithm_type == EnumAlgorithmType.mobile_sam:
            return MobileSAMAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.yolo:
            return YoloAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.rtdetr:
            return RTDETRAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.yolo_classification:
            return YoloClassificationAlgorithm(**model)
        elif algorithm_type == EnumAlgorithmType.easy_ocr:
            return EasyOCRAlgorithm(**model)
