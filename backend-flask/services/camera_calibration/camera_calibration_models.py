from pydantic import BaseModel

from src.utils import CamelModel


class CameraCalibrationParametersModel(BaseModel):
    rows: int
    cols: int
    square_size: float


class CameraIntrinsicsModel(CamelModel):
    uid: str
    camera_matrix: list
    distortion_coeffs: list
