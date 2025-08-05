"""
Hardware Configuration

Centralized hardware configuration for the Industrial Vision Application.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class HardwareConfig(BaseModel):
    """Hardware configuration settings."""
    
    # CNC Configuration
    cnc_enabled: bool = Field(default=True, description="Enable CNC functionality")
    cnc_default_firmware: str = Field(default="grbl", description="Default CNC firmware type")
    cnc_supported_firmwares: List[str] = Field(
        default=["grbl", "marlin", "fluidnc"],
        description="Supported CNC firmware types"
    )
    cnc_poll_interval: float = Field(default=0.2, ge=0.01, le=1.0, description="CNC polling interval in seconds")
    cnc_timeout: int = Field(default=30, ge=1, le=300, description="CNC operation timeout in seconds")
    cnc_max_retries: int = Field(default=3, ge=1, le=10, description="Maximum CNC operation retries")
    cnc_baud_rate: int = Field(default=115200, description="CNC serial baud rate")
    cnc_buffer_size: int = Field(default=128, ge=32, le=1024, description="CNC command buffer size")
    
    # Camera Configuration
    camera_enabled: bool = Field(default=True, description="Enable camera functionality")
    camera_default_backend: str = Field(default="opencv", description="Default camera backend")
    camera_supported_backends: List[str] = Field(
        default=["opencv", "basler", "ethernet"],
        description="Supported camera backends"
    )
    camera_timeout: int = Field(default=5, ge=1, le=60, description="Camera operation timeout in seconds")
    camera_retry_attempts: int = Field(default=3, ge=1, le=10, description="Camera connection retry attempts")
    camera_frame_rate: int = Field(default=30, ge=1, le=120, description="Default camera frame rate")
    camera_resolution_width: int = Field(default=1920, ge=320, le=7680, description="Default camera width")
    camera_resolution_height: int = Field(default=1080, ge=240, le=4320, description="Default camera height")
    camera_auto_exposure: bool = Field(default=True, description="Enable camera auto exposure")
    camera_auto_white_balance: bool = Field(default=True, description="Enable camera auto white balance")
    
    # Robot Configuration
    robot_enabled: bool = Field(default=True, description="Enable robot functionality")
    robot_default_type: str = Field(default="xarm", description="Default robot type")
    robot_supported_types: List[str] = Field(
        default=["xarm", "universal_robots", "kuka", "abb"],
        description="Supported robot types"
    )
    robot_timeout: int = Field(default=30, ge=1, le=300, description="Robot operation timeout in seconds")
    robot_safety_limits: bool = Field(default=True, description="Enable robot safety limits")
    robot_max_velocity: float = Field(default=100.0, ge=1.0, le=1000.0, description="Maximum robot velocity (mm/s)")
    robot_max_acceleration: float = Field(default=500.0, ge=10.0, le=5000.0, description="Maximum robot acceleration (mm/s²)")
    robot_home_position: List[float] = Field(default=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], description="Robot home position")
    
    # Profilometer Configuration
    profilometer_enabled: bool = Field(default=True, description="Enable profilometer functionality")
    profilometer_default_type: str = Field(default="gocator", description="Default profilometer type")
    profilometer_supported_types: List[str] = Field(
        default=["gocator", "keyence", "sick"],
        description="Supported profilometer types"
    )
    profilometer_timeout: int = Field(default=10, ge=1, le=60, description="Profilometer timeout in seconds")
    profilometer_scan_rate: int = Field(default=1000, ge=100, le=10000, description="Profilometer scan rate (Hz)")
    
    # Serial Communication
    serial_timeout: float = Field(default=1.0, ge=0.1, le=60.0, description="Serial communication timeout")
    serial_write_timeout: float = Field(default=1.0, ge=0.1, le=60.0, description="Serial write timeout")
    serial_inter_byte_timeout: Optional[float] = Field(default=None, description="Serial inter-byte timeout")
    serial_exclusive: bool = Field(default=True, description="Exclusive serial port access")
    
    # USB Device Configuration
    usb_scan_interval: int = Field(default=5, ge=1, le=60, description="USB device scan interval in seconds")
    usb_auto_connect: bool = Field(default=True, description="Auto-connect to USB devices")
    usb_vendor_ids: List[str] = Field(
        default=["0x1234", "0x5678"],
        description="Allowed USB vendor IDs"
    )
    
    # Network Device Configuration
    network_scan_enabled: bool = Field(default=True, description="Enable network device scanning")
    network_scan_interval: int = Field(default=30, ge=5, le=300, description="Network scan interval in seconds")
    network_timeout: int = Field(default=5, ge=1, le=30, description="Network device timeout in seconds")
    network_allowed_subnets: List[str] = Field(
        default=["192.168.1.0/24", "10.0.0.0/8"],
        description="Allowed network subnets for device discovery"
    )
    
    # GPIO Configuration (for embedded systems)
    gpio_enabled: bool = Field(default=False, description="Enable GPIO functionality")
    gpio_pins: Dict[str, int] = Field(
        default={
            "emergency_stop": 18,
            "status_led": 19,
            "alarm_output": 20
        },
        description="GPIO pin assignments"
    )
    
    # Performance Settings
    max_concurrent_operations: int = Field(default=5, ge=1, le=50, description="Maximum concurrent hardware operations")
    operation_queue_size: int = Field(default=100, ge=10, le=1000, description="Hardware operation queue size")
    enable_hardware_monitoring: bool = Field(default=True, description="Enable hardware status monitoring")
    monitoring_interval: int = Field(default=10, ge=1, le=300, description="Hardware monitoring interval in seconds")
    
    # Calibration Settings
    auto_calibration_enabled: bool = Field(default=False, description="Enable automatic calibration")
    calibration_interval_hours: int = Field(default=24, ge=1, le=168, description="Calibration interval in hours")
    calibration_tolerance: float = Field(default=0.1, ge=0.001, le=10.0, description="Calibration tolerance")
    
    # Safety Settings
    emergency_stop_enabled: bool = Field(default=True, description="Enable emergency stop functionality")
    safety_interlocks_enabled: bool = Field(default=True, description="Enable safety interlocks")
    motion_limits_enabled: bool = Field(default=True, description="Enable motion limits")
    collision_detection_enabled: bool = Field(default=True, description="Enable collision detection")
    
    # Environmental Monitoring
    temperature_monitoring: bool = Field(default=False, description="Enable temperature monitoring")
    temperature_min: float = Field(default=10.0, description="Minimum operating temperature (°C)")
    temperature_max: float = Field(default=40.0, description="Maximum operating temperature (°C)")
    humidity_monitoring: bool = Field(default=False, description="Enable humidity monitoring")
    humidity_max: float = Field(default=80.0, ge=0.0, le=100.0, description="Maximum operating humidity (%)")
    
    class Config:
        env_prefix = "HARDWARE_"
        case_sensitive = False
    
    @validator("cnc_default_firmware")
    def validate_cnc_firmware(cls, v, values):
        """Validate CNC firmware type."""
        supported = values.get("cnc_supported_firmwares", [])
        if v not in supported:
            raise ValueError(f"CNC firmware must be one of: {supported}")
        return v
    
    @validator("camera_default_backend")
    def validate_camera_backend(cls, v, values):
        """Validate camera backend."""
        supported = values.get("camera_supported_backends", [])
        if v not in supported:
            raise ValueError(f"Camera backend must be one of: {supported}")
        return v
    
    @validator("robot_default_type")
    def validate_robot_type(cls, v, values):
        """Validate robot type."""
        supported = values.get("robot_supported_types", [])
        if v not in supported:
            raise ValueError(f"Robot type must be one of: {supported}")
        return v
    
    @validator("profilometer_default_type")
    def validate_profilometer_type(cls, v, values):
        """Validate profilometer type."""
        supported = values.get("profilometer_supported_types", [])
        if v not in supported:
            raise ValueError(f"Profilometer type must be one of: {supported}")
        return v
    
    @validator("robot_home_position")
    def validate_robot_home_position(cls, v):
        """Validate robot home position."""
        if len(v) != 6:
            raise ValueError("Robot home position must have 6 values (X, Y, Z, Rx, Ry, Rz)")
        return v
    
    @validator("usb_vendor_ids")
    def validate_usb_vendor_ids(cls, v):
        """Validate USB vendor IDs format."""
        validated = []
        for vid in v:
            if not vid.startswith("0x"):
                vid = "0x" + vid
            try:
                int(vid, 16)  # Validate hex format
                validated.append(vid.upper())
            except ValueError:
                raise ValueError(f"Invalid USB vendor ID format: {vid}")
        return validated
    
    def get_cnc_config(self) -> dict:
        """Get CNC configuration."""
        return {
            "enabled": self.cnc_enabled,
            "firmware": self.cnc_default_firmware,
            "supported_firmwares": self.cnc_supported_firmwares,
            "poll_interval": self.cnc_poll_interval,
            "timeout": self.cnc_timeout,
            "max_retries": self.cnc_max_retries,
            "baud_rate": self.cnc_baud_rate,
            "buffer_size": self.cnc_buffer_size,
        }
    
    def get_camera_config(self) -> dict:
        """Get camera configuration."""
        return {
            "enabled": self.camera_enabled,
            "backend": self.camera_default_backend,
            "supported_backends": self.camera_supported_backends,
            "timeout": self.camera_timeout,
            "retry_attempts": self.camera_retry_attempts,
            "frame_rate": self.camera_frame_rate,
            "resolution": {
                "width": self.camera_resolution_width,
                "height": self.camera_resolution_height
            },
            "auto_exposure": self.camera_auto_exposure,
            "auto_white_balance": self.camera_auto_white_balance,
        }
    
    def get_robot_config(self) -> dict:
        """Get robot configuration."""
        return {
            "enabled": self.robot_enabled,
            "type": self.robot_default_type,
            "supported_types": self.robot_supported_types,
            "timeout": self.robot_timeout,
            "safety_limits": self.robot_safety_limits,
            "max_velocity": self.robot_max_velocity,
            "max_acceleration": self.robot_max_acceleration,
            "home_position": self.robot_home_position,
        }
    
    def get_serial_config(self) -> dict:
        """Get serial communication configuration."""
        return {
            "timeout": self.serial_timeout,
            "write_timeout": self.serial_write_timeout,
            "inter_byte_timeout": self.serial_inter_byte_timeout,
            "exclusive": self.serial_exclusive,
        }
    
    def get_safety_config(self) -> dict:
        """Get safety configuration."""
        return {
            "emergency_stop": self.emergency_stop_enabled,
            "safety_interlocks": self.safety_interlocks_enabled,
            "motion_limits": self.motion_limits_enabled,
            "collision_detection": self.collision_detection_enabled,
        }
    
    def get_monitoring_config(self) -> dict:
        """Get monitoring configuration."""
        return {
            "enabled": self.enable_hardware_monitoring,
            "interval": self.monitoring_interval,
            "temperature": {
                "enabled": self.temperature_monitoring,
                "min": self.temperature_min,
                "max": self.temperature_max,
            },
            "humidity": {
                "enabled": self.humidity_monitoring,
                "max": self.humidity_max,
            },
        }

