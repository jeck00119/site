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
    
    # NOTE: USB device detection moved to UnifiedUSBManager in services/port_manager/
    # Use UnifiedUSBManager for all USB-related operations
    
    # NOTE: Camera device detection moved to UnifiedUSBManager in services/port_manager/
    # Use UnifiedUSBManager.get_camera_devices() or get_available_ports_by_type('cameras')


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