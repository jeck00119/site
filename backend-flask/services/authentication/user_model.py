from src.utils import CamelModel


class User(CamelModel):
    uid: str
    username: str
    password: str
    level: str


class UserCredentials(CamelModel):
    username: str
    password: str
