"""
Cross-platform utilities for handling platform-specific operations.
Provides consistent interfaces for Windows and Linux compatibility.
"""
import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PlatformDetector:
    """Utility class for detecting and handling platform differences."""
    
    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows."""
        return platform.system() == "Windows" or sys.platform == "win32" or os.name == "nt"
    
    @staticmethod
    def is_linux() -> bool:
        """Check if running on Linux."""
        return platform.system() == "Linux"
    
    @staticmethod
    def is_macos() -> bool:
        """Check if running on macOS."""
        return platform.system() == "Darwin"
    
    @staticmethod
    def get_platform_name() -> str:
        """Get standardized platform name."""
        if PlatformDetector.is_windows():
            return "Windows"
        elif PlatformDetector.is_linux():
            return "Linux"
        elif PlatformDetector.is_macos():
            return "macOS"
        else:
            return "Unknown"
    
    @staticmethod
    def get_platform_info() -> Dict[str, str]:
        """Get comprehensive platform information."""
        return {
            "system": platform.system(),
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "standardized_name": PlatformDetector.get_platform_name()
        }


class PathHandler:
    """Cross-platform path handling utilities."""
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize path for current platform."""
        return str(Path(path).resolve())
    
    @staticmethod
    def join_paths(*args) -> str:
        """Join paths using platform-appropriate separators."""
        return str(Path(*args))
    
    @staticmethod
    def ensure_directory(path: str) -> str:
        """Ensure directory exists, create if it doesn't."""
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return str(dir_path)
    
    @staticmethod
    def get_project_root() -> str:
        """Get project root directory."""
        # Navigate up from current file to find project root
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent  # Go up two levels from src/
        return str(project_root)
    
    @staticmethod
    def get_data_directory() -> str:
        """Get platform-appropriate data directory."""
        project_root = PathHandler.get_project_root()
        return PathHandler.join_paths(project_root, "data")
    
    @staticmethod
    def get_config_directory() -> str:
        """Get platform-appropriate config directory."""
        project_root = PathHandler.get_project_root()
        return PathHandler.join_paths(project_root, "config_db")
    
    @staticmethod
    def get_reports_directory() -> str:
        """Get platform-appropriate reports directory."""
        project_root = PathHandler.get_project_root()
        return PathHandler.join_paths(project_root, "reports")


class CommandExecutor:
    """Cross-platform command execution utilities."""
    
    @staticmethod
    def run_command(command: List[str], shell: bool = False) -> Tuple[bool, str, str]:
        """
        Run command cross-platform.
        Returns: (success, stdout, stderr)
        """
        try:
            # Platform-specific command execution
            kwargs = {
                'shell': shell,
                'capture_output': True,
                'text': True,
                'timeout': 30
            }
            
            # Windows-specific flags
            if PlatformDetector.is_windows():
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            result = subprocess.run(command, **kwargs)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    @staticmethod
    def kill_process_on_port(port: int) -> bool:
        """
        Kill processes using specified port - cross-platform.
        Returns: True if successful, False otherwise
        """
        try:
            if PlatformDetector.is_windows():
                return CommandExecutor._kill_process_windows(port)
            elif PlatformDetector.is_linux() or PlatformDetector.is_macos():
                return CommandExecutor._kill_process_unix(port)
            else:
                return False
        except Exception:
            return False
    
    @staticmethod
    def _kill_process_windows(port: int) -> bool:
        """Kill process on Windows."""
        try:
            # Find processes using the port
            result = subprocess.run(
                ['netstat', '-ano'], 
                capture_output=True, 
                text=True, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            try:
                                subprocess.run(
                                    ['taskkill', '/F', '/PID', pid], 
                                    capture_output=True,
                                    creationflags=subprocess.CREATE_NO_WINDOW
                                )
                                return True
                            except:
                                pass
            return False
        except:
            return False
    
    @staticmethod
    def _kill_process_unix(port: int) -> bool:
        """Kill process on Unix-like systems (Linux/macOS)."""
        try:
            result = subprocess.run(
                ['lsof', '-Pi', f':{port}', '-sTCP:LISTEN', '-t'], 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid.strip():
                        subprocess.run(['kill', '-9', pid.strip()], capture_output=True)
                        return True
            return False
        except:
            return False
    
    @staticmethod
    def check_usb_devices() -> List[Dict[str, str]]:
        """Check USB devices cross-platform."""
        devices = []
        
        if PlatformDetector.is_windows():
            # Windows USB device detection
            try:
                import win32com.client
                wmi = win32com.client.GetObject("winmgmts:")
                for usb in wmi.InstancesOf("Win32_USBHub"):
                    if usb.DeviceID:
                        devices.append({
                            "id": usb.DeviceID,
                            "name": usb.Name or "Unknown",
                            "platform": "Windows"
                        })
            except ImportError:
                # Fallback if win32com is not available
                pass
        
        elif PlatformDetector.is_linux():
            # Linux USB device detection using lsusb
            success, stdout, stderr = CommandExecutor.run_command(["lsusb"])
            if success:
                for line in stdout.splitlines():
                    if "ID " in line:
                        parts = line.split()
                        if len(parts) >= 6:
                            device_id = parts[5]  # Extract ID like "046d:085e"
                            name = " ".join(parts[6:]) if len(parts) > 6 else "Unknown"
                            devices.append({
                                "id": device_id,
                                "name": name,
                                "platform": "Linux"
                            })
        
        elif PlatformDetector.is_macos():
            # macOS USB device detection using system_profiler
            success, stdout, stderr = CommandExecutor.run_command([
                "system_profiler", "SPUSBDataType", "-xml"
            ])
            if success:
                # Parse XML output for USB devices
                # This is a simplified version - could be enhanced with XML parsing
                devices.append({
                    "id": "macos_usb_detection",
                    "name": "macOS USB Detection Available",
                    "platform": "macOS"
                })
        
        return devices
    
    @staticmethod
    def check_camera_devices() -> List[Dict[str, any]]:
        """Check camera devices cross-platform."""
        cameras = []
        
        if PlatformDetector.is_windows():
            # Windows camera detection
            try:
                import win32com.client
                wmi = win32com.client.GetObject("winmgmts:")
                for usb in wmi.InstancesOf("Win32_USBHub"):
                    if usb.DeviceID and ('vid_046d' in usb.DeviceID.lower() or 'vid_045e' in usb.DeviceID.lower()):
                        cameras.append({
                            "id": usb.DeviceID,
                            "name": usb.Name or "Unknown Camera",
                            "platform": "Windows",
                            "available": True
                        })
            except ImportError:
                pass
        
        elif PlatformDetector.is_linux():
            # Linux camera detection
            usb_devices = CommandExecutor.check_usb_devices()
            for device in usb_devices:
                # Check for common camera vendor IDs
                if any(vid in device["id"].lower() for vid in ["046d", "045e"]):  # Logitech, Microsoft
                    cameras.append({
                        "id": device["id"],
                        "name": device["name"],
                        "platform": "Linux",
                        "available": True
                    })
            
            # Also check /dev/video* devices
            video_devices = []
            for i in range(10):  # Check video0 through video9
                video_path = f"/dev/video{i}"
                if os.path.exists(video_path):
                    video_devices.append({
                        "id": f"video{i}",
                        "name": f"Video Device {i}",
                        "platform": "Linux",
                        "path": video_path,
                        "available": True
                    })
            cameras.extend(video_devices)
        
        elif PlatformDetector.is_macos():
            # macOS camera detection
            success, stdout, stderr = CommandExecutor.run_command([
                "system_profiler", "SPCameraDataType"
            ])
            if success:
                # Parse camera information from system_profiler output
                cameras.append({
                    "id": "macos_camera_detection",
                    "name": "macOS Camera Detection Available",
                    "platform": "macOS",
                    "available": True
                })
        
        return cameras


class PlatformSpecificConfig:
    """Platform-specific configuration management."""
    
    @staticmethod
    def get_opencv_camera_backend():
        """Get appropriate OpenCV camera backend for platform."""
        if PlatformDetector.is_windows():
            return "CAP_DSHOW"  # DirectShow for Windows
        elif PlatformDetector.is_linux():
            return "CAP_V4L2"   # Video4Linux2 for Linux
        else:
            return "CAP_ANY"    # Default backend
    
    @staticmethod
    def get_platform_dependencies() -> List[str]:
        """Get platform-specific Python dependencies."""
        base_deps = [
            "fastapi",
            "uvicorn",
            "opencv-python",
            "numpy",
            "pydantic"
        ]
        
        if PlatformDetector.is_windows():
            base_deps.extend([
                "pywin32",  # For Windows WMI access
            ])
        elif PlatformDetector.is_linux():
            base_deps.extend([
                # Linux-specific packages if needed
            ])
        
        return base_deps
    
    @staticmethod
    def setup_environment():
        """Setup platform-specific environment variables."""
        if PlatformDetector.is_windows():
            # Windows-specific environment setup
            os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
            
            # Set console to UTF-8 for emoji support
            try:
                os.system("chcp 65001 > nul")
            except:
                pass
        
        elif PlatformDetector.is_linux():
            # Linux-specific environment setup
            pass


# Convenience functions for easy imports
def get_platform() -> str:
    """Get current platform name."""
    return PlatformDetector.get_platform_name()

def is_windows() -> bool:
    """Check if running on Windows."""
    return PlatformDetector.is_windows()

def is_linux() -> bool:
    """Check if running on Linux."""
    return PlatformDetector.is_linux()

def is_macos() -> bool:
    """Check if running on macOS."""
    return PlatformDetector.is_macos()

def normalize_path(path: str) -> str:
    """Normalize path for current platform."""
    return PathHandler.normalize_path(path)

def join_paths(*args) -> str:
    """Join paths using platform-appropriate separators."""
    return PathHandler.join_paths(*args)

def ensure_directory(path: str) -> str:
    """Ensure directory exists."""
    return PathHandler.ensure_directory(path)