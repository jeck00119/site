from services.algorithms.algorithms_models import EnumAlgorithmType, EnumReferenceAlgorithmType
from services.algorithms.models.aruco_detector_algorithm_model import ArucoDetectorAlgorithmModel
from services.algorithms.models.barcode_scan_algorithm_model import BarcodeScanAlgorithmModel
from services.algorithms.models.basic_binarization_algorithm_model import BasicBinarizationAlgorithmModel
from services.algorithms.models.brightness_averaging_algorithm_model import BrightnessAveragingAlgorithmModel
from services.algorithms.models.cable_cover_detection_algorithm_model import CableCoverDetectionAlgorithmModel
from services.algorithms.models.cable_detection_yolov8_algorithm_model import CableDetectionYoloV8AlgorithmModel
from services.algorithms.models.cable_inspection_algorithm_model import CableInspectionAlgorithmModel
from services.algorithms.models.circle_detection_ransac_algorithm_model import CircleDetectionRansacAlgorithmModel
from services.algorithms.models.clips_reference_algorithm_model import ClipsReferenceAlgorithmModel
from services.algorithms.models.clips_shut_algorithm_model import ClipsShutAlgorithmModel
from services.algorithms.models.color_averaging_algorithm_model import ColorAveragingAlgorithmModel
from services.algorithms.models.color_matcher_algorithm_model import ColorMatcherAlgorithmModel
from services.algorithms.models.conformal_hsv_algorithm_model import ConformalHSVAlgorithmModel
from services.algorithms.models.contour_double_algorithm_model import ContourDoubleAlgorithmModel
from services.algorithms.models.contour_double_hsv_algorithm_model import ContourDoubleHSVAlgorithmModel
from services.algorithms.models.contour_gravity_center_algorithm_model import ContourGravityCenterAlgorithmModel
from services.algorithms.models.contour_logic_algorithm_model import ContourLogicAlgorithmModel
from services.algorithms.models.dmc_algorithm_model import DmcAlgorithmModel
from services.algorithms.models.easy_ocr_algorithm_model import EasyOCRAlgorithmModel
from services.algorithms.models.foreground_subtraction_algorithm_model import ForegroundSubtractionAlgorithmModel
from services.algorithms.models.graph_segmentation_algorithm_model import GraphSegmentationAlgorithmModel
from services.algorithms.models.horizontal_line_position_algorithm_model import HorizontalLinePositionAlgorithmModel
from services.algorithms.models.label_detection_algorithm_model import LabelDetectionAlgorithmModel
from services.algorithms.models.line_reference_algorithm_model import LineReferenceAlgorithmModel
from services.algorithms.models.mobile_sam_algorithm_model import MobileSAMAlgorithmModel
from services.algorithms.models.motion_detection_hist_algorithm_model import MotionDetectionHistAlgorithmModel
from services.algorithms.models.ocr_algorithm_model import OCRAlgorithmModel
from services.algorithms.models.rtdetr_algorithm_model import RTDETRAlgorithmModel
from services.algorithms.models.sam_algorithm_model import SAMAlgorithmModel
from services.algorithms.models.scratch_detection_template_algorithm_model import ScratchDetectionTemplateAlgorithmModel
from services.algorithms.models.simple_histogram_algorithm_model import SimpleHistogramAlgorithmModel
from services.algorithms.models.steep_detection_algorithm_model import SteepDetectionAlgorithmModel
from services.algorithms.models.template_detection_algorithm_model import TemplateDetectionAlgorithmModel
from services.algorithms.models.vertical_line_position_algorithm_model import VerticalLinePositionAlgorithmModel
from services.algorithms.models.yolo_algorithm_model import YoloAlgorithmModel
from services.algorithms.models.yolo_classification_model import YoloClassificationAlgorithmModel


class ModelsFactory(object):
    @staticmethod
    def create_model(algorithm_type):
        if algorithm_type == EnumAlgorithmType.basic_binarization:
            return BasicBinarizationAlgorithmModel()
        if algorithm_type == EnumAlgorithmType.dmc:
            return DmcAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.simple_histogram:
            return SimpleHistogramAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.motion_detection_hist:
            return MotionDetectionHistAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.color_averaging:
            return ColorAveragingAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.brightness_averaging:
            return BrightnessAveragingAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.conformal_hsv:
            return ConformalHSVAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.contour_logic:
            return ContourLogicAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.barcode_scan:
            return BarcodeScanAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.steep_detection:
            return SteepDetectionAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.ocr:
            return OCRAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.contour_double:
            return ContourDoubleAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.contour_double_hsv:
            return ContourDoubleHSVAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.aruco_detector:
            return ArucoDetectorAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.color_matcher:
            return ColorMatcherAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.clips_shut:
            return ClipsShutAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.foreground_subtraction:
            return ForegroundSubtractionAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.graph_segmentation:
            return GraphSegmentationAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.label:
            return LabelDetectionAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.cable_inspection:
            return CableInspectionAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.cable_cover:
            return CableCoverDetectionAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.scratch_template:
            return ScratchDetectionTemplateAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.contour_gravity_center:
            return ContourGravityCenterAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.sam:
            return SAMAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.cable_detection_yolov8:
            return CableDetectionYoloV8AlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.mobile_sam:
            return MobileSAMAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.yolo:
            return YoloAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.rtdetr:
            return RTDETRAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.yolo_classification:
            return YoloClassificationAlgorithmModel()
        elif algorithm_type == EnumAlgorithmType.easy_ocr:
            return EasyOCRAlgorithmModel()
        elif algorithm_type == EnumReferenceAlgorithmType.circle_detection_ransac:
            return CircleDetectionRansacAlgorithmModel()
        elif algorithm_type == EnumReferenceAlgorithmType.template_detection:
            return TemplateDetectionAlgorithmModel()
        elif algorithm_type == EnumReferenceAlgorithmType.line_reference:
            return LineReferenceAlgorithmModel()
        elif algorithm_type == EnumReferenceAlgorithmType.vertical_line:
            return VerticalLinePositionAlgorithmModel()
        elif algorithm_type == EnumReferenceAlgorithmType.horizontal_line:
            return HorizontalLinePositionAlgorithmModel()
        elif algorithm_type == EnumReferenceAlgorithmType.clips_reference:
            return ClipsReferenceAlgorithmModel()
