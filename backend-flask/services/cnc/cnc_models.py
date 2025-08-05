from typing import Any

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


class LocationModel(CamelModel):
    uid: Any
    axis_uid: Any
    degree_in_step: Any
    feedrate: Any
    name: Any
    x: Any
    y: Any
    z: Any