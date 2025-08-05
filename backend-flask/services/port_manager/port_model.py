from typing import Any

from src.utils import CamelModel


class PortModel(CamelModel):
    uid: Any
    port: Any
    cnc_type: Any
        