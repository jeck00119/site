from typing import List

from repo.repositories import RobotRepository
from services.robot.robot_builder import RobotBuilder
from services.robot.robot_models import RobotModel
from src.metaclasses.singleton import Singleton
from src.utils import generate_uid
import logging


class RobotService(metaclass=Singleton):
    def __init__(self, offline: bool = False):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.robot_repository = RobotRepository()
        self.robots = {}  # Active robot instances
        self.offline = offline

    def get_available_types(self):
        """Get available robot types."""
        return ["xArm", "ultraArm"]

    def start_robot_service(self):
        """Start the robot service and initialize all robots."""
        try:
            self.logger.info("Starting robot service...")
            robot_models = self.robot_repository.read_all()
            for robot_data in robot_models:
                robot_uid = robot_data.get('uid')
                if robot_uid:
                    self.initialize_robot(robot_uid)
            self.logger.info(f"Robot service started with {len(robot_models)} robots")
        except Exception as e:
            self.logger.error(f"Error starting robot service: {e}")

    def update_robots(self, robot_models: List[RobotModel]):
        """Update robots and return add, update, delete lists."""
        try:
            existing_robots = {robot['uid']: robot for robot in self.robot_repository.read_all()}
            new_robot_uids = {robot.uid for robot in robot_models}
            existing_uids = set(existing_robots.keys())
            
            add = new_robot_uids - existing_uids
            update = new_robot_uids & existing_uids
            delete = existing_uids - new_robot_uids
            
            self.logger.info(f"Robot update: add={len(add)}, update={len(update)}, delete={len(delete)}")
            return list(add), list(update), list(delete)
            
        except Exception as e:
            self.logger.error(f"Error updating robots: {e}")
            return [], [], []

    def get_angles(self, robot_uid: str):
        """Get current robot angles."""
        try:
            if robot_uid in self.robots:
                robot = self.robots[robot_uid]
                if hasattr(robot, 'get_angles'):
                    return robot.get_angles()
                elif hasattr(robot, 'get_position'):
                    return robot.get_position()
            
            # Return default angles if robot not found or not initialized
            self.logger.warning(f"Robot {robot_uid} not found, returning default angles")
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            
        except Exception as e:
            self.logger.error(f"Error getting angles for robot {robot_uid}: {e}")
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def move_to_position(self, robot_uid: str, angles: List[float], speed: float = None):
        """Move robot to specified position."""
        try:
            if robot_uid not in self.robots:
                self.logger.warning(f"Robot {robot_uid} not initialized")
                return False
                
            robot = self.robots[robot_uid]
            if hasattr(robot, 'move_to_position'):
                return robot.move_to_position(angles, speed)
            elif hasattr(robot, 'set_position'):
                return robot.set_position(angles, speed=speed)
            else:
                self.logger.warning(f"Robot {robot_uid} does not support position movement")
                return False
                
        except Exception as e:
            self.logger.error(f"Error moving robot {robot_uid}: {e}")
            return False

    def home(self, robot_uid: str):
        """Home the robot."""
        try:
            if robot_uid not in self.robots:
                self.logger.warning(f"Robot {robot_uid} not initialized")
                return False
                
            robot = self.robots[robot_uid]
            if hasattr(robot, 'home'):
                return robot.home()
            elif hasattr(robot, 'go_home'):
                return robot.go_home()
            else:
                self.logger.warning(f"Robot {robot_uid} does not support homing")
                return False
                
        except Exception as e:
            self.logger.error(f"Error homing robot {robot_uid}: {e}")
            return False

    def set_angle_on_joint(self, robot_uid: str, joint_number: int, angle: float, speed: float = None):
        """Set angle on specific joint."""
        try:
            if robot_uid not in self.robots:
                self.logger.warning(f"Robot {robot_uid} not initialized")
                return False
                
            robot = self.robots[robot_uid]
            if hasattr(robot, 'set_joint_angle'):
                return robot.set_joint_angle(joint_number, angle, speed)
            elif hasattr(robot, 'set_angle'):
                return robot.set_angle(joint_number, angle, speed)
            else:
                self.logger.warning(f"Robot {robot_uid} does not support joint angle setting")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting joint angle for robot {robot_uid}: {e}")
            return False

    def release_servos(self, robot_uid: str):
        """Release robot servos."""
        try:
            if robot_uid not in self.robots:
                self.logger.warning(f"Robot {robot_uid} not initialized")
                return False
                
            robot = self.robots[robot_uid]
            if hasattr(robot, 'release_servos'):
                return robot.release_servos()
            elif hasattr(robot, 'disable_motors'):
                return robot.disable_motors()
            else:
                self.logger.warning(f"Robot {robot_uid} does not support servo release")
                return False
                
        except Exception as e:
            self.logger.error(f"Error releasing servos for robot {robot_uid}: {e}")
            return False

    def power_servos(self, robot_uid: str):
        """Power on robot servos."""
        try:
            if robot_uid not in self.robots:
                self.logger.warning(f"Robot {robot_uid} not initialized")
                return False
                
            robot = self.robots[robot_uid]
            if hasattr(robot, 'power_servos'):
                return robot.power_servos()
            elif hasattr(robot, 'enable_motors'):
                return robot.enable_motors()
            else:
                self.logger.warning(f"Robot {robot_uid} does not support servo power")
                return False
                
        except Exception as e:
            self.logger.error(f"Error powering servos for robot {robot_uid}: {e}")
            return False

    def initialize_robot(self, robot_uid: str):
        """Initialize a robot."""
        try:
            robot_doc = self.robot_repository.read_id(robot_uid)
            if not robot_doc:
                self.logger.error(f"Robot {robot_uid} not found in database")
                return False
                
            robot_model = RobotModel(**robot_doc)
            
            if self.offline:
                # Create mock robot for offline mode
                robot = self._create_mock_robot(robot_model)
            else:
                robot = RobotBuilder.create_robot(robot_model)
                
            if robot:
                self.robots[robot_uid] = robot
                self.logger.info(f"Robot {robot_uid} initialized successfully")
                return True
            else:
                self.logger.error(f"Failed to create robot instance for {robot_uid}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error initializing robot {robot_uid}: {e}")
            return False

    def _create_mock_robot(self, robot_model: RobotModel):
        """Create a mock robot for offline mode."""
        class MockRobot:
            def __init__(self, model):
                self.model = model
                self.angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                
            def get_angles(self):
                return self.angles
                
            def move_to_position(self, angles, speed=None):
                self.angles = angles[:6] if len(angles) >= 6 else angles + [0.0] * (6 - len(angles))
                return True
                
            def home(self):
                self.angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                return True
                
            def set_joint_angle(self, joint_number, angle, speed=None):
                if 0 <= joint_number < len(self.angles):
                    self.angles[joint_number] = angle
                    return True
                return False
                
            def release_servos(self):
                return True
                
            def power_servos(self):
                return True
                
        return MockRobot(robot_model)

