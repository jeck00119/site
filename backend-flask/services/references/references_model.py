from typing import Any

from src.utils import generate_uid, CamelModel


class ReferenceModel(CamelModel):
    uid: str = generate_uid(length=8)
    name: str
    image_source_uid: Any
    algorithm_uid: Any
    algorithm_type: Any
