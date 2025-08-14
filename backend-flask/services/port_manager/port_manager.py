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
        # Device type configurations - 5 main categories: CNCs, Cameras, DMC readers, Ultra Arm robots, Profilometers
        self.device_types = {
            'cncs': {
                'description_patterns': [
                    "Arduino Uno", "USB-SERIAL CH340", 
                    "USB Serial Port", "MARLIN_STM32G0B1RE CDC in FS",
                    "Arduino", "CH340", "CP210", "FTDI", "PL2303", "CDC",
                    "STMicroelectronics", "Virtual COM Port", "Grbl", "Marlin"
                ],
                'device_patterns': ['usb', 'acm', 'serial', 'ch340', 'cp210', 'ftdi'],
                'industrial_terms': ['arduino', 'marlin', 'grbl', 'ch340', 'cp210', 'ftdi', 'stm32', 'virtual com port']
            },
            'dmc_readers': {
                'description_patterns': [
                    "Cognex", "DataMan", "DMC Reader", "Barcode Scanner", "Code Reader"
                ],
                'vid_pid_pairs': [
                    {'vid': 0x1447, 'pid': 0x8022},  # Cognex DataMan specific VID:PID
                    {'vid': 0x1447, 'pid': None}     # Any Cognex device
                ]
            },
            'ultra_arm_robots': {
                'description_patterns': [
                    "Ultra Arm", "Robot Arm", "Robotic Arm", "UltraArm"
                ],
                'vid_pid_pairs': [
                    {'vid': 6790, 'pid': 29987}  # Ultra Arm specific VID:PID
                ]
            },
            'cameras': {
                'description_patterns': [
                    "Camera", "Webcam", "Video", "Imaging", "Capture", 
                    "Logitech", "Microsoft LifeCam"
                ],
                'vid_pid_pairs': [
                    {'vid': 0x046d, 'pid': None},  # Logitech (any PID)
                    {'vid': 0x045e, 'pid': None},  # Microsoft (any PID)
                    {'vid': 0x0c45, 'pid': None},  # Microdia (any PID)
                ]
            },
            'profilometers': {
                'description_patterns': [
                    "Keyence", "SICK", "Profilometer", "Laser Scanner", 
                    "3D Scanner", "Profile Scanner"
                ],
                'vid_pid_pairs': [
                    # Add specific VID/PID pairs for known profilometer manufacturers
                    # These would need to be added based on actual hardware
                ]
            },
            # Legacy compatibility
            'serial_communication': {
                'description_patterns': [
                    "Arduino Uno", "USB-SERIAL CH340", 
                    "USB Serial Port", "MARLIN_STM32G0B1RE CDC in FS",
                    "Arduino", "CH340", "CP210", "FTDI", "PL2303", "CDC",
                    "STMicroelectronics", "Virtual COM Port", "Grbl", "Marlin"
                ],
                'device_patterns': ['usb', 'acm', 'serial', 'ch340', 'cp210', 'ftdi']
            },
            'cognex_cameras': {
                'vid_pid_pairs': [
                    {'vid': 0x1447, 'pid': 0x8022}  # Cognex specific VID:PID - legacy
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
        """Classify what type(s) of device this USB port represents - 5 main categories."""
        device_types = []
        
        # Priority order: DMC readers, Ultra Arm robots, Profilometers, CNCs, then Cameras (to avoid conflicts)
        
        # 1. Check DMC readers (Cognex) first - most specific
        if self._is_dmc_reader(comport):
            device_types.append('dmc_readers')
            # Legacy compatibility
            device_types.append('cognex_cameras')
        
        # 2. Check Ultra Arm robots
        elif self._is_ultra_arm_robot(comport):
            device_types.append('ultra_arm_robots')
        
        # 3. Check Profilometers (Keyence, SICK, etc.)
        elif self._is_profilometer_device(comport):
            device_types.append('profilometers')
        
        # 4. Check CNCs (only if not already classified)
        elif self._is_cnc_device(comport):
            device_types.append('cncs')
            # Legacy compatibility
            device_types.append('serial_communication')
        
        # 5. Check Cameras (only if not classified as anything else)
        elif self._is_camera_device(comport):
            device_types.append('cameras')
        
        return device_types

    def _is_cnc_device(self, comport) -> bool:
        """Check if device is a CNC machine (Marlin, GRBL, etc.)."""
        if not comport.device:
            return False
            
        config = self.device_types['cncs']
        
        # Check description patterns for known CNC/industrial devices
        if comport.description:
            description_lower = comport.description.lower()
            for pattern in config['description_patterns']:
                if pattern.lower() in description_lower:
                    return True
        
        # More restrictive VID/PID check - only if description suggests industrial use
        if comport.vid and comport.pid and comport.vid > 0 and comport.pid > 0:
            if comport.description:
                desc_lower = comport.description.lower()
                
                # Exclude generic USB serial devices that are likely non-CNC
                if desc_lower == "usb serial device":
                    return False
                
                # Check for industrial terms
                if any(term in desc_lower for term in config['industrial_terms']):
                    return True
        
        # Check device name patterns (cross-platform)
        device_lower = comport.device.lower()
        if any(pattern in device_lower for pattern in config['device_patterns']):
            return True
            
        return False
    
    def _is_dmc_reader(self, comport) -> bool:
        """Check if device is a DMC reader (Cognex DataMan, etc.)."""
        if not comport.device:
            return False
            
        config = self.device_types['dmc_readers']
        
        # First exclude generic devices that are definitely not DMC readers
        if comport.description:
            desc_lower = comport.description.lower()
            # Don't classify generic USB serial devices as DMC readers
            if desc_lower == "usb serial device":
                return False
        
        # Check description patterns for specific DMC reader terms
        if comport.description:
            description_lower = comport.description.lower()
            for pattern in config['description_patterns']:
                if pattern.lower() in description_lower:
                    return True
        
        # Check VID:PID pairs (more reliable for Cognex devices)
        if self._matches_vid_pid(comport, config['vid_pid_pairs']):
            return True
            
        return False
    
    def _is_ultra_arm_robot(self, comport) -> bool:
        """Check if device is an Ultra Arm robot."""
        if not comport.device:
            return False
            
        config = self.device_types['ultra_arm_robots']
        
        # Check description patterns
        if comport.description:
            description_lower = comport.description.lower()
            for pattern in config['description_patterns']:
                if pattern.lower() in description_lower:
                    return True
        
        # Check VID:PID pairs (most reliable for Ultra Arm)
        if self._matches_vid_pid(comport, config['vid_pid_pairs']):
            return True
            
        return False
    
    def _is_profilometer_device(self, comport) -> bool:
        """Check if device is a profilometer (Keyence, SICK, etc.)."""
        if not comport.device:
            return False
            
        config = self.device_types['profilometers']
        
        # Check description patterns
        if comport.description:
            description_lower = comport.description.lower()
            for pattern in config['description_patterns']:
                if pattern.lower() in description_lower:
                    return True
        
        # Check VID:PID pairs
        if self._matches_vid_pid(comport, config['vid_pid_pairs']):
            return True
            
        return False
    
    def _is_camera_device(self, comport) -> bool:
        """Check if device is a camera (webcam, USB camera, etc.)."""
        if not comport.device:
            return False
            
        config = self.device_types['cameras']
        
        # Check description patterns
        if comport.description:
            description_lower = comport.description.lower()
            for pattern in config['description_patterns']:
                if pattern.lower() in description_lower:
                    return True
        
        # Check VID:PID pairs
        if self._matches_vid_pid(comport, config['vid_pid_pairs']):
            return True
            
        return False

    # Legacy compatibility method
    def _is_serial_device(self, comport) -> bool:
        """Legacy method - check if device is suitable for serial communication (CNCs)."""
        return self._is_cnc_device(comport)

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

    # === MAIN CATEGORY METHODS ===

    async def get_cnc_devices(self) -> List[Dict[str, Any]]:
        """Get all CNC devices (Marlin, GRBL, etc.)."""
        return await self.get_devices_by_type('cncs')

    async def get_dmc_reader_devices(self) -> List[Dict[str, Any]]:
        """Get all DMC reader devices (Cognex DataMan, etc.)."""
        return await self.get_devices_by_type('dmc_readers')

    async def get_ultra_arm_robot_devices(self) -> List[Dict[str, Any]]:
        """Get all Ultra Arm robot devices."""
        return await self.get_devices_by_type('ultra_arm_robots')

    async def get_camera_devices(self) -> List[Dict[str, Any]]:
        """Get all camera devices (webcams, USB cameras, etc.)."""
        return await self.get_devices_by_type('cameras')

    async def get_profilometer_devices(self) -> List[Dict[str, Any]]:
        """Get all profilometer devices (Keyence, SICK, etc.)."""
        return await self.get_devices_by_type('profilometers')

    async def get_available_ports_by_type(self, device_type: str) -> List[Dict[str, Any]]:
        """Get available ports for a specific device type - unified method."""
        return await self.get_devices_by_type(device_type)

    async def get_cnc_ports(self) -> List[str]:
        """Get CNC port device names with descriptions."""
        devices = await self.get_cnc_devices()
        port_list = []
        for device in devices:
            port = device['device']
            description = device.get('description', '')
            if description:
                # Clean up common long descriptions
                if 'STMicroelectronics' in description:
                    clean_name = 'STMicroelectronics'
                elif 'Arduino' in description:
                    clean_name = 'Arduino'
                elif 'CH340' in description:
                    clean_name = 'CH340'
                else:
                    clean_name = description.split('(')[0].strip()[:20]
                port_display = f"{port} ({clean_name})"
            else:
                port_display = port
            port_list.append(port_display)
        return port_list

    async def get_dmc_reader_ports(self) -> List[str]:
        """Get DMC reader port device names with descriptions."""
        devices = await self.get_dmc_reader_devices()
        port_list = []
        for device in devices:
            port = device['device']
            description = device.get('description', '')
            if description:
                # Clean up descriptions for DMC readers
                if 'Cognex' in description:
                    clean_name = 'Cognex DMC Reader'
                elif 'DataMan' in description:
                    clean_name = 'DataMan'
                else:
                    clean_name = description.split('(')[0].strip()[:20]
                port_display = f"{port} ({clean_name})"
            else:
                port_display = port
            port_list.append(port_display)
        return port_list

    async def get_ultra_arm_robot_ports(self) -> List[str]:
        """Get Ultra Arm robot port device names with descriptions."""
        devices = await self.get_ultra_arm_robot_devices()
        port_list = []
        for device in devices:
            port = device['device']
            description = device.get('description', '')
            if description:
                # Clean up descriptions for Ultra Arm robots
                if 'Ultra Arm' in description:
                    clean_name = 'Ultra Arm Robot'
                elif 'Robot' in description:
                    clean_name = 'Robot Arm'
                else:
                    clean_name = description.split('(')[0].strip()[:20]
                port_display = f"{port} ({clean_name})"
            else:
                port_display = port
            port_list.append(port_display)
        return port_list

    # === LEGACY COMPATIBILITY METHODS ===

    async def get_cognex_devices(self) -> List[Dict[str, Any]]:
        """Get Cognex camera devices (legacy - use get_dmc_reader_devices instead)."""
        return await self.get_devices_by_type('cognex_cameras')

    async def is_cognex_connected(self) -> bool:
        """Check if any Cognex device is connected (legacy - use DMC reader methods instead)."""
        cognex_devices = await self.get_cognex_devices()
        return len(cognex_devices) > 0

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

    async def validate_port_for_cnc(self, port: str) -> Dict[str, Any]:
        """
        Validate if a port is suitable for CNC connection.
        Returns validation result with device type information.
        """
        # Get the actual port name (remove description if present)
        actual_port = port.split('(')[0].strip() if '(' in port else port
        
        result = {
            'is_valid': False,
            'is_cnc_device': False,
            'device_types': [],
            'device_description': '',
            'error_message': '',
            'suggested_action': ''
        }
        
        try:
            # Find the device information
            all_devices = await self.get_all_usb_devices()
            port_device = None
            for device in all_devices:
                if device['device'] == actual_port:
                    port_device = device
                    break
            
            if port_device:
                device_types = port_device['device_types']
                result['device_types'] = device_types
                result['device_description'] = port_device['description']
                
                # Check if port is actually a CNC device
                if 'cncs' in device_types:
                    result['is_valid'] = True
                    result['is_cnc_device'] = True
                    result['error_message'] = f"Port {actual_port} validated as CNC device"
                else:
                    result['is_valid'] = False
                    result['is_cnc_device'] = False
                    
                    if 'dmc_readers' in device_types:
                        result['error_message'] = f"Port {actual_port} is a DMC reader (Cognex), not a CNC device"
                        result['suggested_action'] = "Please select a CNC port instead"
                    elif 'cameras' in device_types:
                        result['error_message'] = f"Port {actual_port} is a camera device, not a CNC device"
                        result['suggested_action'] = "Please select a CNC port instead"
                    elif 'ultra_arm_robots' in device_types:
                        result['error_message'] = f"Port {actual_port} is an Ultra Arm robot, not a CNC device"
                        result['suggested_action'] = "Please select a CNC port instead"
                    else:
                        device_type_str = ', '.join(device_types) if device_types else 'unknown device type'
                        result['error_message'] = f"Port {actual_port} is not a CNC device (detected as: {device_type_str})"
                        result['suggested_action'] = "Please select a CNC port"
            else:
                result['error_message'] = f"Port {actual_port} not found in available USB devices"
                result['suggested_action'] = "Check if device is connected and try again"
                
        except Exception as e:
            result['error_message'] = f"Port validation failed: {str(e)}"
            result['suggested_action'] = "Connection will be attempted anyway"
        
        return result

    async def validate_port_for_device_type(self, port: str, expected_device_type: str) -> Dict[str, Any]:
        """
        Universal device validation method - works for all device types.
        
        Args:
            port: Port string (e.g., "COM11 (USB Serial Device)" or "COM10")
            expected_device_type: One of 'cncs', 'dmc_readers', 'ultra_arm_robots', 'cameras'
        
        Returns:
            Dict with validation results including error messages and suggestions
        """
        # Map device types to user-friendly names
        device_type_names = {
            'cncs': 'CNC machine',
            'dmc_readers': 'DMC reader (Cognex)',
            'ultra_arm_robots': 'Ultra Arm robot',
            'cameras': 'camera device',
            'profilometers': 'profilometer (Keyence/SICK)',
            'serial_communication': 'serial device'  # Legacy compatibility
        }
        
        # Get the actual port name (remove description if present)
        actual_port = port.split('(')[0].strip() if '(' in port else port
        expected_name = device_type_names.get(expected_device_type, expected_device_type)
        
        result = {
            'is_valid': False,
            'is_correct_device_type': False,
            'expected_device_type': expected_device_type,
            'expected_device_name': expected_name,
            'actual_device_types': [],
            'actual_device_name': '',
            'device_description': '',
            'error_message': '',
            'suggested_action': '',
            'port': actual_port
        }
        
        try:
            # Find the device information
            all_devices = await self.get_all_usb_devices()
            port_device = None
            for device in all_devices:
                if device['device'] == actual_port:
                    port_device = device
                    break
            
            if port_device:
                device_types = port_device['device_types']
                result['actual_device_types'] = device_types
                result['device_description'] = port_device['description']
                
                # Check if port has the expected device type
                if expected_device_type in device_types:
                    result['is_valid'] = True
                    result['is_correct_device_type'] = True
                    result['error_message'] = f"Port {actual_port} validated as {expected_name}"
                else:
                    result['is_valid'] = False
                    result['is_correct_device_type'] = False
                    
                    # Determine what device type is actually connected
                    if 'dmc_readers' in device_types:
                        result['actual_device_name'] = 'DMC reader (Cognex)'
                    elif 'cncs' in device_types:
                        result['actual_device_name'] = 'CNC machine'
                    elif 'ultra_arm_robots' in device_types:
                        result['actual_device_name'] = 'Ultra Arm robot'
                    elif 'profilometers' in device_types:
                        result['actual_device_name'] = 'profilometer (Keyence/SICK)'
                    elif 'cameras' in device_types:
                        result['actual_device_name'] = 'camera device'
                    else:
                        result['actual_device_name'] = ', '.join(device_types) if device_types else 'unknown device'
                    
                    result['error_message'] = (
                        f"Configuration mismatch: Expected {expected_name} on port {actual_port}, "
                        f"but found {result['actual_device_name']} instead"
                    )
                    result['suggested_action'] = f"Please update configuration to use the correct port for {expected_name}"
            else:
                result['error_message'] = f"Port {actual_port} not found or not connected"
                result['suggested_action'] = f"Check if {expected_name} is connected and try again"
                
        except Exception as e:
            result['error_message'] = f"Port validation failed: {str(e)}"
            result['suggested_action'] = "Connection will be attempted anyway"
        
        return result

    # Keep the CNC-specific method for backward compatibility
    async def validate_port_for_cnc(self, port: str) -> Dict[str, Any]:
        """Validate port for CNC connection - uses universal validation method."""
        universal_result = await self.validate_port_for_device_type(port, 'cncs')
        
        # Convert to old format for backward compatibility
        return {
            'is_valid': universal_result['is_valid'],
            'is_cnc_device': universal_result['is_correct_device_type'],
            'device_types': universal_result['actual_device_types'],
            'device_description': universal_result['device_description'],
            'error_message': universal_result['error_message'],
            'suggested_action': universal_result['suggested_action']
        }

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
            'profilometers': 0,
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
