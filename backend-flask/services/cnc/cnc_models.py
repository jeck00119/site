from typing import Any, List
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
    x: float
    y: float
    z: float
    feedrate: int = Field(default=1500)


class SequenceModel(CamelModel):
    uid: str
    cnc_uid: str  
    name: str
    items: List[dict] = Field(default_factory=list)