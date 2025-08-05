from src.utils import CamelModel


class ItacModel(CamelModel):
    name: str
    destination_ip: str
    destination_port: str
    start_booking_code: str
    pass_booking_code: str
    fail_booking_code: str
    uid: str
