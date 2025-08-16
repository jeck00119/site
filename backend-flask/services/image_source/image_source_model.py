from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel

from src.utils import generate_uid


class ImgSrcEnum(str, Enum):
    DYNAMIC = 'dynamic'
    STATIC = 'static'


class ImageSourceModel(BaseModel):
    uid: Any = generate_uid(length=8)
    name: str = f'ImageSource{uid}'

    image_source_type: ImgSrcEnum
    camera_uid: Any
    camera_settings_uid: Any
    camera_calibration_uid: Optional[Any] = None
    image_generator_uid: Any

    location_name: Any
    settle_time: Any
    activate_location: Any

    fps: Any
