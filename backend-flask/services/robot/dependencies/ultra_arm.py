from pymycobot.ultraArm import ultraArm


class UltraArm:
    def __init__(self, port):
        self.arm = None
        self.port = port

    def get_connection_id(self):
        return self.port

    def initialize(self):
        self.arm = ultraArm(self.port, 115200)

    def home(self):
        if self.arm:
            self.arm.go_zero()

    def initial_position(self):
        if self.arm:
            self.arm.set_angles([0.0, 0.0, 0.0], 100)

    def go_to_pos(self, x: float, y: float, z: float, speed: int):
        if self.arm:
            self.arm.set_coords([x, y, z], speed)

    def set_speed_mode(self, mode):
        if self.arm:
            self.arm.set_speed_mode(mode)

    def set_angle(self, joint_number, angle, speed):
        if self.arm:
            self.arm.set_angle(joint_number, angle, speed)

    def set_angles(self, angles, speed):
        if self.arm:
            self.arm.set_angles(angles, speed)

    def get_coords(self):
        return self.arm.get_coords_info()

    def release_callback(self):
        if self.arm:
            self.arm.close()

    def set_callback(self):
        pass

    def clean_warning(self):
        pass

    def get_angles_info(self):
        if self.arm:
            return self.arm.get_angles_info()

        return None

    def power_servos(self):
        if self.arm:
            self.arm.power_on()

    def release_servos(self):
        if self.arm:
            self.arm.release_all_servos()
