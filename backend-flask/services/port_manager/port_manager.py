import serial.tools.list_ports
import re
from typing import List, Dict, Optional, Any

from src.metaclasses.singleton import Singleton
from src.platform_utils import PlatformDetector


class UnifiedUSBManager(metaclass=Singleton):
    """
    Unified USB device detection and management system.
    Handles all USB device types: serial ports, cameras, industrial hardware.
    Replaces duplicate USB detection code across the application.
    """
    def __init__(self):
        # Device type configurations
        self.device_types = {
            'serial_communication': {
                'description_patterns': [
                    "Arduino Uno", "USB Serial Device", "USB-SERIAL CH340", 
                    "USB Serial Port", "MARLIN_STM32G0B1RE CDC in FS",
                    "Arduino", "CH340", "CP210", "FTDI", "PL2303", "CDC"
                ],
                'device_patterns': ['usb', 'acm', 'serial', 'ch340', 'cp210', 'ftdi']
            },
            'cognex_cameras': {
                'vid_pid_pairs': [
                    {'vid': 0x1447, 'pid': 0x8022}  # Cognex specific VID:PID
                ]
            },
            'ultra_arm_robots': {
                'vid_pid_pairs': [
                    {'vid': 6790, 'pid': 29987}  # Ultra Arm specific VID:PID
                ]
            },
            'cameras': {
                'vid_pid_pairs': [
                    {'vid': 0x046d, 'pid': None},  # Logitech (any PID)
                    {'vid': 0x045e, 'pid': None},  # Microsoft (any PID)
                    {'vid': 0x0c45, 'pid': None},  # Microdia (any PID)
                ]
            }
        }

    def _create_device_info(self, comport) -> Dict[str, Any]:
        """Create standardized device information dictionary."""
        return {
            'device': comport.device,
            'description': comport.description or 'Unknown Device',
            'manufacturer': comport.manufacturer or 'Unknown',
            'vid': comport.vid,
            'pid': comport.pid,
            'vid_hex': f"0x{comport.vid:04X}" if comport.vid else None,
            'pid_hex': f"0x{comport.pid:04X}" if comport.pid else None,
            'serial_number': comport.serial_number,
            'location': comport.location,
            'device_types': self._classify_device(comport)
        }

    def _classify_device(self, comport) -> List[str]:
        """Classify what type(s) of device this USB port represents."""
        device_types = []
        
        # Check serial communication devices
        if self._is_serial_device(comport):
            device_types.append('serial_communication')
        
        # Check Cognex cameras
        if self._matches_vid_pid(comport, self.device_types['cognex_cameras']['vid_pid_pairs']):
            device_types.append('cognex_cameras')
        
        # Check Ultra Arm robots
        if self._matches_vid_pid(comport, self.device_types['ultra_arm_robots']['vid_pid_pairs']):
            device_types.append('ultra_arm_robots')
        
        # Check general cameras
        if self._matches_vid_pid(comport, self.device_types['cameras']['vid_pid_pairs']):
            device_types.append('cameras')
        
        return device_types

    def _is_serial_device(self, comport) -> bool:
        """Check if device is suitable for serial communication."""
        if not comport.device:
            return False
            
        config = self.device_types['serial_communication']
        
        # Check description patterns
        if comport.description:
            description_lower = comport.description.lower()
            for pattern in config['description_patterns']:
                if pattern.lower() in description_lower:
                    return True
        
        # Check for valid VID/PID (exclude built-in ports)
        if comport.vid and comport.pid and comport.vid > 0 and comport.pid > 0:
            return True
        
        # Check device name patterns (cross-platform)
        device_lower = comport.device.lower()
        if any(pattern in device_lower for pattern in config['device_patterns']):
            return True
            
        return False

    def _matches_vid_pid(self, comport, vid_pid_pairs: List[Dict]) -> bool:
        """Check if device matches any of the specified VID:PID pairs."""
        if not comport.vid or not comport.pid:
            return False
            
        for pair in vid_pid_pairs:
            vid_match = comport.vid == pair['vid']
            pid_match = pair['pid'] is None or comport.pid == pair['pid']
            
            if vid_match and pid_match:
                return True
        
        return False

    # === UNIFIED USB DEVICE DETECTION METHODS ===

    async def get_all_usb_devices(self) -> List[Dict[str, Any]]:
        """Get comprehensive information about all USB devices."""
        devices = []
        for comport in serial.tools.list_ports.comports():
            device_info = self._create_device_info(comport)
            devices.append(device_info)
        
        return sorted(devices, key=lambda x: x['device'])

    async def get_devices_by_type(self, device_type: str) -> List[Dict[str, Any]]:
        """Get devices of a specific type."""
        all_devices = await self.get_all_usb_devices()
        return [device for device in all_devices if device_type in device['device_types']]

    # === LEGACY COMPATIBILITY METHODS (for existing code) ===

    async def get_available_ports(self) -> List[str]:
        """Get serial port device names for CNC/industrial devices with descriptions."""
        devices = await self.get_devices_by_type('serial_communication')
        port_list = []
        for device in devices:
            port = device['device']
            description = device.get('description', '')
            # Create enhanced port display: "COM10 (STMicroelectronics)" or just "COM10" if no description
            if description:
                # Clean up common long descriptions
                if 'STMicroelectronics' in description:
                    clean_name = 'STMicroelectronics'
                elif 'Cognex' in description:
                    clean_name = 'Cognex Camera'
                elif 'Arduino' in description:
                    clean_name = 'Arduino'
                elif 'USB Serial' in description:
                    clean_name = 'USB Serial Device'
                elif 'Logitech' in description or 'LogiCam' in description:
                    clean_name = 'Logitech Camera'
                else:
                    # Take first 20 chars and clean up
                    clean_name = description.split('(')[0].strip()[:20]
                port_display = f"{port} ({clean_name})"
            else:
                port_display = port
            port_list.append(port_display)
        return port_list

    async def get_available_ports_detailed(self) -> List[Dict[str, Any]]:
        """Get detailed information about serial communication ports."""
        return await self.get_devices_by_type('serial_communication')

    async def get_available_ports_ultra_arm(self) -> List[str]:
        """Get Ultra Arm robot ports with device names."""
        devices = await self.get_devices_by_type('ultra_arm_robots')
        port_list = []
        for device in devices:
            port = device['device']
            description = device.get('description', '')
            if description:
                # Clean up description for Ultra Arm devices
                if 'Ultra Arm' in description:
                    clean_name = 'Ultra Arm Robot'
                elif 'Arduino' in description:
                    clean_name = 'Arduino'
                else:
                    clean_name = description.split('(')[0].strip()[:20]
                port_display = f"{port} ({clean_name})"
            else:
                port_display = port
            port_list.append(port_display)
        return port_list

    # === NEW UNIFIED METHODS ===

    async def get_cognex_devices(self) -> List[Dict[str, Any]]:
        """Get Cognex camera devices."""
        return await self.get_devices_by_type('cognex_cameras')

    async def is_cognex_connected(self) -> bool:
        """Check if any Cognex device is connected."""
        cognex_devices = await self.get_cognex_devices()
        return len(cognex_devices) > 0

    async def get_camera_devices(self) -> List[Dict[str, Any]]:
        """Get all camera devices (including Cognex)."""
        cameras = await self.get_devices_by_type('cameras')
        cognex = await self.get_devices_by_type('cognex_cameras')
        return cameras + cognex

    async def get_robot_devices(self) -> List[Dict[str, Any]]:
        """Get all robot devices (Ultra Arm, etc.)."""
        return await self.get_devices_by_type('ultra_arm_robots')

    async def get_device_by_vid_pid(self, vid: int, pid: int) -> Optional[Dict[str, Any]]:
        """Find device by specific VID:PID pair."""
        all_devices = await self.get_all_usb_devices()
        for device in all_devices:
            if device['vid'] == vid and device['pid'] == pid:
                return device
        return None

    # === CROSS-PLATFORM PORT COMPATIBILITY ===

    def is_windows_port(self, port: str) -> bool:
        """Check if port path is Windows format (COMx)."""
        import re
        return bool(re.match(r'^COM\d+$', port.upper()))

    def is_linux_port(self, port: str) -> bool:
        """Check if port path is Linux format (/dev/ttyXXXX)."""
        return port.startswith('/dev/tty')

    def is_macos_port(self, port: str) -> bool:
        """Check if port path is macOS format (/dev/cu.XXX or /dev/tty.XXX)."""
        return port.startswith('/dev/cu.') or port.startswith('/dev/tty.')

    def get_current_platform(self) -> str:
        """Get current platform identifier using centralized platform detection."""
        if PlatformDetector.is_windows():
            return 'windows'
        elif PlatformDetector.is_macos():
            return 'macos'
        elif PlatformDetector.is_linux():
            return 'linux'
        else:
            return 'unknown'

    async def validate_port_compatibility(self, port: str) -> Dict[str, Any]:
        """
        Validate if a port is compatible with the current platform.
        Returns validation result with suggestions for cross-platform issues.
        """
        current_platform = self.get_current_platform()
        available_ports = await self.get_available_ports()
        
        result = {
            'is_valid': False,
            'is_cross_platform_issue': False,
            'current_platform': current_platform,
            'port_platform': None,
            'available_ports': available_ports,
            'suggested_ports': [],
            'message': ''
        }

        # Determine port platform
        if self.is_windows_port(port):
            result['port_platform'] = 'windows'
        elif self.is_linux_port(port):
            result['port_platform'] = 'linux'
        elif self.is_macos_port(port):
            result['port_platform'] = 'macos'
        else:
            result['port_platform'] = 'unknown'

        # Check if port is directly available (exact match)
        port_only = port.split('(')[0].strip() if '(' in port else port
        available_ports_clean = [p.split('(')[0].strip() for p in available_ports]
        
        if port_only in available_ports_clean:
            result['is_valid'] = True
            result['message'] = f"Port {port} is available and compatible"
            return result

        # Check for cross-platform issues
        if result['port_platform'] != current_platform and result['port_platform'] != 'unknown':
            result['is_cross_platform_issue'] = True
            result['suggested_ports'] = available_ports[:3]  # Suggest first 3 available ports
            
            platform_names = {
                'windows': 'Windows',
                'linux': 'Linux', 
                'macos': 'macOS'
            }
            
            result['message'] = (
                f"Port '{port}' is configured for {platform_names.get(result['port_platform'], result['port_platform'])} "
                f"but you're running on {platform_names.get(current_platform, current_platform)}. "
                f"Available ports: {', '.join(available_ports[:3])}"
            )
        else:
            result['message'] = f"Port '{port}' is not available. Available ports: {', '.join(available_ports[:3])}"

        return result

    # === DEBUGGING AND ADMIN METHODS ===

    async def get_all_ports(self) -> List[Dict[str, Any]]:
        """Get all USB devices with classification info (for debugging)."""
        devices = await self.get_all_usb_devices()
        
        # Add legacy 'valid' field for backward compatibility
        for device in devices:
            device['valid'] = 'serial_communication' in device['device_types']
        
        return devices

    async def get_device_summary(self) -> Dict[str, int]:
        """Get summary count of different device types."""
        all_devices = await self.get_all_usb_devices()
        summary = {
            'total_devices': len(all_devices),
            'serial_communication': 0,
            'cognex_cameras': 0,
            'ultra_arm_robots': 0,
            'cameras': 0,
            'unclassified': 0
        }
        
        for device in all_devices:
            device_types = device['device_types']
            if not device_types:
                summary['unclassified'] += 1
            else:
                for device_type in device_types:
                    if device_type in summary:
                        summary[device_type] += 1
        
        return summary


# Backward compatibility alias
PortManager = UnifiedUSBManager


# if __name__ == "__main__":
#     for comport in serial.tools.list_ports.comports():
#         par_ind = comport.description.rfind(" ")
#         device_name = comport.description[:par_ind]
