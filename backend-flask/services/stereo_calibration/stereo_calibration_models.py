from typing import Optional

from src.utils import CamelModel


class StereoResultsModel(CamelModel):
    uid: str
    first_image_src_uid: str
    second_image_src_uid: str
    R0: list
    T0: list
    R1: list
    T1: list
    world_to_cam_left_rot: Optional[list]
    world_to_cam_left_trans: Optional[list]
    world_to_cam_right_rot: Optional[list]
    world_to_cam_right_trans: Optional[list]
    essential_matrix: list
    fundamental_matrix: list
