from typing import Any, List, Optional
from pydantic import Field

from src.utils import CamelModel


class CncFeedbackModel(CamelModel):
    cnc_state: Any
    x_pos: Any


class CncModel(CamelModel):
    uid: Any
    name: Any
    # Types can be "GRBL", "FluidNC", or "Marlin"
    type: Any
    port: Any
    sequences: List[dict] = Field(default_factory=list)  # List of saved position sequences
    shortcuts: List[dict] = Field(default_factory=list)  # List of saved location shortcuts
    
    # 3D CNC Setup Configuration
    x_axis_length: int = Field(default=300)  # X-axis physical travel length in mm
    y_axis_length: int = Field(default=300)  # Y-axis physical travel length in mm  
    z_axis_length: int = Field(default=100)  # Z-axis physical travel length in mm
    working_zone_x: int = Field(default=250)  # Usable X working area in mm
    working_zone_y: int = Field(default=250)  # Usable Y working area in mm
    working_zone_z: int = Field(default=80)   # Usable Z working area in mm
    selected_axes: dict = Field(default_factory=lambda: {"x": True, "y": True, "z": True})  # Active axes selection


class LocationModel(CamelModel):
    uid: Any
    axis_uid: Any
    degree_in_step: Any
    feedrate: Any
    name: Any
    x: Any
    y: Any
    z: Any


class SequenceItemModel(CamelModel):
    location_uid: str = ""
    name: str
    # Coordinates are optional for backward compatibility
    # New format stores only locationUid and resolves coordinates from LocationRepository
    x: Optional[float] = Field(default=None)
    y: Optional[float] = Field(default=None) 
    z: Optional[float] = Field(default=None)
    feedrate: int = Field(default=1500)


class SequenceModel(CamelModel):
    uid: str
    cnc_uid: str  
    name: str
    items: List[dict] = Field(default_factory=list)