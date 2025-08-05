from typing import Any

from src.utils import CamelModel


class ImageGeneratorModel(CamelModel):
    uid: Any
    dir_path: str

