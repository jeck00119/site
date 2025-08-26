"""
Image Stitching Service Module

Provides image capture and panorama stitching capabilities for CNC mapping operations.
"""

from .image_stitching_service import (
    ImageStitchingService,
    ImageStitchingError,
    StitchingConfigurationError,
    StitchingCaptureError,
    StitchingProcessError
)
from .image_stitching_models import (
    ImageStitchingConfigModel,
    StitchingSessionModel,
    StitchingStatus,
    StitchingPattern,
    CapturePositionModel,
    CapturedImageModel,
    StitchingProgressModel,
    StitchingResultModel
)

__all__ = [
    'ImageStitchingService',
    'ImageStitchingConfigModel',
    'StitchingSessionModel', 
    'StitchingStatus',
    'StitchingPattern',
    'CapturePositionModel',
    'CapturedImageModel',
    'StitchingProgressModel',
    'StitchingResultModel',
    'StitchingConfigurationError',
    'StitchingCaptureError', 
    'StitchingProcessError',
    'ImageStitchingError'
]