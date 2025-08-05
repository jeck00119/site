from enum import Enum

from pydantic import field_validator

from services.algorithms.models.aruco_detector_algorithm_model import ArucoDetectorAlgorithmModel
from services.algorithms.models.barcode_scan_algorithm_model import BarcodeScanAlgorithmModel
from services.algorithms.models.basic_binarization_algorithm_model import BasicBinarizationAlgorithmModel
from services.algorithms.models.blob_detection_algorithm_model import BlobDetectionAlgorithmModel
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
from services.algorithms.models.steep_detection_algorithm_model import SteepDetectionAlgorithmModel
from services.algorithms.models.template_detection_algorithm_model import TemplateDetectionAlgorithmModel
from services.algorithms.models.vertical_line_position_algorithm_model import VerticalLinePositionAlgorithmModel
from services.algorithms.models.yolo_algorithm_model import YoloAlgorithmModel
from services.algorithms.models.yolo_classification_model import YoloClassificationAlgorithmModel
from src.utils import generate_uid, CamelModel


class EnumAlgorithmType(str, Enum):
    basic_binarization = "Basic Binarization Algorithm"
    dmc = "DMC Algorithm"
    simple_histogram = "Simple Histogram"
    motion_detection_hist = "Motion Detection Histogram"
    color_averaging = "Color Averaging"
    brightness_averaging = "Brightness Averaging"
    conformal_hsv = "Conformal HSV"
    contour_logic = "Contour Logic"
    barcode_scan = "Barcode Scan"
    steep_detection = "Steep Detection"
    ocr = "OCR"
    contour_double = "Contour Double"
    contour_double_hsv = "Contour Double HSV"
    aruco_detector = "Aruco Detector"
    color_matcher = "Color Matcher"
    clips_shut = "Clips Shut"
    foreground_subtraction = "Foreground Subtraction"
    graph_segmentation = "Graph Segmentation"
    label = "Label"
    cable_inspection = "Cable Inspection"
    cable_cover = "Cable Cover"
    scratch_template = "Scratch Template"
    contour_gravity_center = "Contour Gravity Center"
    blob = "Blob"
    sam = "SAM"
    cable_detection_yolov8 = "Cable YOLO v8"
    mobile_sam = "Mobile SAM"
    yolo = "YOLO"
    rtdetr = "RTDETR"
    yolo_classification = "YOLO Classification"
    easy_ocr = "Easy OCR"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class EnumReferenceAlgorithmType(str, Enum):
    contour_gravity_center = "Contour Gravity Center"
    circle_detection_ransac = "Circle Detection Ransac"
    template_detection = "Template Detection"
    line_reference = "Line Reference"
    vertical_line = "Vertical Line"
    horizontal_line = "Horizontal Line"
    clips_reference = "Clips Reference"
    yolo = "YOLO"
    rtdetr = "RTDETR"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class AlgorithmModel(CamelModel):
    uid: str = generate_uid(length=8)
    type: str
    name: str = f'Algorithm_{uid}'
    parameters: dict

    @field_validator('parameters')
    @classmethod
    def match_parameters(cls, v, info):
        if info.data['type'] == EnumAlgorithmType.basic_binarization.value:
            return BasicBinarizationAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.dmc.value:
            return DmcAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.simple_histogram.value:
            return DmcAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.motion_detection_hist.value:
            return MotionDetectionHistAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.color_averaging.value:
            return ColorAveragingAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.brightness_averaging.value:
            return BrightnessAveragingAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.conformal_hsv.value:
            return ConformalHSVAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.contour_logic.value:
            return ContourLogicAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.barcode_scan.value:
            return BarcodeScanAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.steep_detection.value:
            return SteepDetectionAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.ocr.value:
            return OCRAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.contour_double.value:
            return ContourDoubleAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.contour_double_hsv.value:
            return ContourDoubleHSVAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.aruco_detector.value:
            return ArucoDetectorAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.color_matcher.value:
            return ColorMatcherAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.clips_shut.value:
            return ClipsShutAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.foreground_subtraction.value:
            return ForegroundSubtractionAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.graph_segmentation.value:
            return GraphSegmentationAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.label.value:
            return LabelDetectionAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.cable_inspection.value:
            return CableInspectionAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.cable_cover.value:
            return CableCoverDetectionAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.scratch_template.value:
            return ScratchDetectionTemplateAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.contour_gravity_center.value:
            return ContourGravityCenterAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.blob:
            return BlobDetectionAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.sam.value:
            return SAMAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.cable_detection_yolov8.value:
            return CableDetectionYoloV8AlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.mobile_sam.value:
            return MobileSAMAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.yolo:
            return YoloAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.rtdetr:
            return RTDETRAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.yolo_classification:
            return YoloClassificationAlgorithmModel(**v)
        elif info.data['type'] == EnumAlgorithmType.easy_ocr:
            return EasyOCRAlgorithmModel(**v)
        elif info.data['type'] == EnumReferenceAlgorithmType.circle_detection_ransac.value:
            return CircleDetectionRansacAlgorithmModel(**v)
        elif info.data['type'] == EnumReferenceAlgorithmType.template_detection.value:
            return TemplateDetectionAlgorithmModel(**v)
        elif info.data['type'] == EnumReferenceAlgorithmType.line_reference.value:
            return LineReferenceAlgorithmModel(**v)
        elif info.data['type'] == EnumReferenceAlgorithmType.vertical_line.value:
            return VerticalLinePositionAlgorithmModel(**v)
        elif info.data['type'] == EnumReferenceAlgorithmType.horizontal_line.value:
            return HorizontalLinePositionAlgorithmModel(**v)
        elif info.data['type'] == EnumReferenceAlgorithmType.clips_reference.value:
            return ClipsReferenceAlgorithmModel(**v)
