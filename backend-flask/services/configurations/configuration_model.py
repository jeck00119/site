from src.utils import CamelModel


class ConfigurationModel(CamelModel):
    name: str
    type: str
    part_number: str
    uid: str
