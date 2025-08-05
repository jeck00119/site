from services.robot.dependencies.ultra_arm import UltraArm
from services.robot.dependencies.xarm_robot import XArmRobot, XArmRobotDummy


class RobotBuilder:
    XARM = "xArm"
    XARM_DUMMY = "xArmDummy"
    ULTRA_ARM = "ultraArm"

    @staticmethod
    def create_robot(robot_type: str, data: [None, dict] = None):
        if robot_type in RobotBuilder.XARM:
            return XArmRobot(ip_robot=data["ip"])
        elif robot_type in RobotBuilder.XARM_DUMMY:
            return XArmRobotDummy()
        elif robot_type in RobotBuilder.ULTRA_ARM:
            return UltraArm(port=data["port"])
        else:
            return None
