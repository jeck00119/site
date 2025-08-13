from typing import Optional
from src.utils import CamelModel


class Entry(CamelModel):
    pass


class AppEntry(Entry):
    timestamp: str
    user: str
    type: str
    title: str
    description: str
    details: Optional[str] = None
