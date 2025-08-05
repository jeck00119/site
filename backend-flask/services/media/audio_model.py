from src.utils import CamelModel


class AudioModel(CamelModel):
    name: str
    path: str
    timeout: int
    channel: int
    priority: int
    volume: int

