# Cross-Platform Setup Guide

This guide will help you set up the AOI Web Application on both Windows and Linux platforms.

## Prerequisites

### Windows
- Python 3.8+ ([Download from python.org](https://www.python.org/downloads/))
- Node.js 16+ ([Download from nodejs.org](https://nodejs.org/))
- Git for Windows ([Download](https://git-scm.com/download/win))

### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install system dependencies for camera support
sudo apt-get install v4l-utils libv4l-dev

# Install USB utilities
sudo apt-get install usbutils

# Add user to dialout group for USB device access
sudo usermod -a -G dialout $USER
# Log out and log back in for this to take effect
```

### Linux (CentOS/RHEL/Fedora)
```bash
# For CentOS/RHEL
sudo yum install python3 python3-pip
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs
sudo yum install v4l-utils v4l2-devel usbutils

# For Fedora
sudo dnf install python3 python3-pip nodejs npm
sudo dnf install v4l-utils v4l2-devel usbutils

# Add user to dialout group
sudo usermod -a -G dialout $USER
```

## Quick Start

### Automated Startup (Recommended)

#### Windows
1. Double-click `start_backend.bat` to start the backend server
2. Double-click `start_frontend.bat` to start the frontend development server

#### Linux
1. Run `./start_backend.sh` to start the backend server
2. Run `./start_frontend.sh` to start the frontend development server

### Manual Setup

#### Backend Setup

##### Windows
```cmd
cd backend-flask
python -m venv venv
venv\Scripts\activate
pip install -r requirements-windows.txt
python main.py
```

##### Linux
```bash
cd backend-flask
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-linux.txt
python main.py
```

#### Frontend Setup

##### Both Platforms
```bash
cd aoi-web-front
npm install
npm run dev
```

## Platform-Specific Features

### Windows
- **Camera Support**: Uses DirectShow backend for webcam access
- **USB Device Detection**: Uses Windows Management Instrumentation (WMI)
- **Hardware Access**: Native Windows API support

### Linux
- **Camera Support**: Uses Video4Linux2 (V4L2) backend
- **USB Device Detection**: Uses `lsusb` command and udev
- **Hardware Access**: Requires user to be in `dialout` group

## Environment Configuration

The application automatically detects the platform and configures itself accordingly:

- **Path Handling**: Uses platform-appropriate path separators
- **Camera Backends**: Automatically selects DirectShow (Windows) or V4L2 (Linux)
- **USB Detection**: Platform-specific device enumeration
- **Console Output**: UTF-8 encoding support on Windows

## Troubleshooting

### Common Issues

#### Camera Not Detected
- **Windows**: Ensure camera drivers are installed
- **Linux**: Check if user is in `dialout` group and `/dev/video0` exists

#### USB Device Access Denied
- **Windows**: Run as administrator if needed
- **Linux**: Ensure user is in `dialout` group

#### Port Already in Use
The application automatically finds available ports in the range 8000-8010.

#### Python Import Errors
- Ensure virtual environment is activated
- Install platform-specific requirements file

### Platform-Specific Debugging

#### Windows
```cmd
# Check camera devices
wmic path CIM_LogicalDevice where "Description like 'USB%'" get /value

# Check USB devices
wmic path Win32_USBHub get DeviceID, Name
```

#### Linux
```bash
# Check camera devices
ls -la /dev/video*
v4l2-ctl --list-devices

# Check USB devices
lsusb
lsusb -v

# Check user groups
groups $USER
```

## Development Notes

### Cross-Platform Code
- Use `src/platform_utils.py` for platform-specific operations
- All file paths use the `PathHandler` utility
- Camera creation uses the `CameraFactory` with automatic platform detection

### Adding New Platform-Specific Features
1. Update `src/platform_utils.py` with new detection logic
2. Add platform-specific implementations in appropriate service classes
3. Update requirements files if new dependencies are needed
4. Test on both platforms

## System Requirements

### Minimum
- **RAM**: 4GB
- **CPU**: Dual-core 2.0GHz
- **Storage**: 2GB free space
- **USB**: USB 2.0 for camera and device connections

### Recommended
- **RAM**: 8GB+
- **CPU**: Quad-core 2.5GHz+
- **Storage**: 5GB+ free space
- **USB**: USB 3.0 for better camera performance

## Support

For platform-specific issues:
1. Check this guide first
2. Review the logs for platform detection messages
3. Ensure all prerequisites are installed
4. Try the manual setup process to isolate issues

The application logs will show which platform was detected and any platform-specific initialization steps.