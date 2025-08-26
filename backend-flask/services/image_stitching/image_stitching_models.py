from typing import List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field


class StitchingStatus(str, Enum):
    """Status of the stitching process"""
    IDLE = "idle"
    CAPTURING = "capturing" 
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class StitchingPattern(str, Enum):
    """Pattern for image capture"""
    ZIGZAG = "zigzag"
    RASTER = "raster"


class ImageStitchingConfigModel(BaseModel):
    """Configuration for image stitching process"""
    uid: str = Field(..., description="Unique identifier for the stitching session")
    step_size_x: float = Field(..., ge=1.0, le=50.0, description="X step size in mm")
    step_size_y: float = Field(..., ge=1.0, le=50.0, description="Y step size in mm") 
    z_height: float = Field(..., ge=5.0, le=100.0, description="Camera Z height in mm")
    overlap_percent: float = Field(..., ge=20.0, le=60.0, description="Overlap percentage between images")
    pattern: StitchingPattern = Field(default=StitchingPattern.ZIGZAG, description="Capture pattern")
    working_area_x: float = Field(..., ge=0.0, description="Working area X dimension in mm")
    working_area_y: float = Field(..., ge=0.0, description="Working area Y dimension in mm")
    camera_uid: str = Field(..., description="Camera UID to use for capture")


class CapturePositionModel(BaseModel):
    """Position for image capture"""
    x: float = Field(..., description="X coordinate in mm")
    y: float = Field(..., description="Y coordinate in mm") 
    z: float = Field(..., description="Z coordinate in mm")
    sequence_index: int = Field(..., ge=0, description="Index in capture sequence")


class CapturedImageModel(BaseModel):
    """Captured image metadata"""
    uid: str = Field(..., description="Unique identifier for the image")
    position: CapturePositionModel = Field(..., description="Capture position")
    timestamp: float = Field(..., description="Capture timestamp")
    file_path: str = Field(..., description="Path to saved image file")
    camera_uid: str = Field(..., description="Camera UID used for capture")


class StitchingSessionModel(BaseModel):
    """Complete stitching session data"""
    uid: str = Field(..., description="Session unique identifier")
    config: ImageStitchingConfigModel = Field(..., description="Stitching configuration")
    status: StitchingStatus = Field(default=StitchingStatus.IDLE, description="Current status")
    captured_images: List[CapturedImageModel] = Field(default_factory=list, description="Captured images")
    total_positions: int = Field(default=0, description="Total positions to capture")
    completed_positions: int = Field(default=0, description="Completed positions")
    result_image_path: Optional[str] = Field(default=None, description="Path to stitched result image")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: float = Field(..., description="Session creation timestamp")
    started_at: Optional[float] = Field(default=None, description="Capture start timestamp")
    completed_at: Optional[float] = Field(default=None, description="Completion timestamp")


class StitchingProgressModel(BaseModel):
    """Progress information for stitching process"""
    session_uid: str = Field(..., description="Session unique identifier")
    status: StitchingStatus = Field(..., description="Current status")
    progress_percent: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    current_position: Optional[CapturePositionModel] = Field(default=None, description="Current capture position")
    completed_positions: int = Field(..., ge=0, description="Number of completed positions")
    total_positions: int = Field(..., ge=0, description="Total positions to capture")
    message: str = Field(default="", description="Status message")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")


class StitchingResultModel(BaseModel):
    """Result of the stitching process"""
    session_uid: str = Field(..., description="Session unique identifier")
    success: bool = Field(..., description="Whether stitching was successful")
    result_image_path: Optional[str] = Field(default=None, description="Path to stitched image")
    result_image_url: Optional[str] = Field(default=None, description="URL to download stitched image")
    captured_image_count: int = Field(..., ge=0, description="Number of images captured")
    processing_time_seconds: Optional[float] = Field(default=None, description="Processing time in seconds")
    image_dimensions: Optional[Tuple[int, int]] = Field(default=None, description="Result image dimensions (width, height)")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")