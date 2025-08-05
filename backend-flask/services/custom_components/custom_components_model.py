from src.utils import generate_uid, CamelModel


class CustomComponentModel(CamelModel):
    uid: str = generate_uid(length=8)
    name: str
    image_source_uid: str
    algorithms: list
    blocks: list
