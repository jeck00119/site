import logging
import asyncio
from services.robot.dependencies.ultra_arm import UltraArm
from services.robot.dependencies.xarm_robot import XArmRobot, XArmRobotDummy


class RobotBuilder:
    XARM = "xArm"
    XARM_DUMMY = "xArmDummy"  
    ULTRA_ARM = "ultraArm"

    @staticmethod
    def create_robot(robot_model):
        """Create robot with universal port validation."""
        logger = logging.getLogger(__name__)
        
        try:
            robot_type = robot_model.type
            
            # Validate port for Ultra Arm robots (they use serial ports)
            if robot_type == RobotBuilder.ULTRA_ARM:
                try:
                    from services.port_manager.port_manager import UnifiedUSBManager
                    
                    port_manager = UnifiedUSBManager()
                    
                    # Use universal validation method
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    validation_result = loop.run_until_complete(
                        port_manager.validate_port_for_device_type(robot_model.port, 'ultra_arm_robots')
                    )
                    loop.close()
                    
                    logger.info(f"Robot {robot_model.uid}: {validation_result['error_message']}")
                    
                    if not validation_result['is_valid']:
                        error_msg = f"{validation_result['error_message']}. {validation_result['suggested_action']}"
                        logger.error(f"Robot {robot_model.uid}: {error_msg}")
                        raise Exception(error_msg)
                        
                except ImportError:
                    logger.warning(f"Robot {robot_model.uid}: Port manager not available - skipping port validation")
                except Exception as validation_error:
                    logger.warning(f"Robot {robot_model.uid}: Port validation failed: {validation_error}")
                    # Don't raise the exception, let connection be attempted
            
            # Create the robot instance
            if robot_type == RobotBuilder.XARM:
                return XArmRobot(ip_robot=robot_model.ip)
            elif robot_type == RobotBuilder.XARM_DUMMY:
                return XArmRobotDummy()
            elif robot_type == RobotBuilder.ULTRA_ARM:
                return UltraArm(port=robot_model.port)
            else:
                logger.error(f"Unknown robot type: {robot_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create robot: {e}")
            return None
