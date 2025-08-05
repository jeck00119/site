from typing import List

from src.utils import CamelModel


class RobotModel(CamelModel):
    uid: str
    name: str
    type: str

    def get_connection_id(self):
        pass


class XArmModel(RobotModel):
    ip: str

    def get_connection_id(self):
        return self.ip


class UltraArmModel(RobotModel):
    port: str

    def get_connection_id(self):
        return self.port


class RobotList(CamelModel):
    robots: List[RobotModel]


class RobotPositionsModel(CamelModel):
    uid: str
    angles: list
    components: list
    speed: int
    robot_uid: str
    name: str
