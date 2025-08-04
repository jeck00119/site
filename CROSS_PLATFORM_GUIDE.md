# 🌐 Cross-Platform Setup Guide

This guide provides detailed instructions for setting up the CNC Control System on different operating systems.

## 🖥️ Platform Support

- ✅ **Windows 10/11** (x64)
- ✅ **Linux** (Ubuntu 18.04+, Debian 10+, CentOS 7+, Fedora 30+, Arch Linux)
- ✅ **macOS** (10.15+)

## 🚀 Quick Platform Detection

Run this command to detect your platform and get specific instructions:

```bash
python setup.py
```

The setup script automatically detects your platform and provides tailored installation steps.

## 🪟 Windows Setup

### Prerequisites

1. **Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - ⚠️ **Important**: Check "Add Python to PATH" during installation

2. **Node.js 16+**
   - Download from [nodejs.org](https://nodejs.org/)
   - Choose LTS version for best compatibility

3. **Git** (optional)
   - Download from [git-scm.com](https://git-scm.com/)

4. **Visual C++ Build Tools** (for some packages)
   - Download from [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Or install Visual Studio Community with C++ workload

### Installation Steps

1. **Run system dependencies installer:**
   ```cmd
   install-system-deps.bat
   ```

2. **Run automated setup:**
   ```cmd
   python setup.py
   ```

3. **Start the application:**
   ```cmd
   start_cnc_system.bat
   ```

### Windows-Specific Issues

**PowerShell Execution Policy:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Package compilation errors:**
```cmd
# Use Windows-specific requirements
pip install -r requirements-windows.txt
```

**Serial port permissions:**
- No special permissions needed
- Ports appear as COM1, COM2, etc.

## 🐧 Linux Setup

### Prerequisites Installation

1. **Run system dependencies installer:**
   ```bash
   chmod +x install-system-deps.sh
   ./install-system-deps.sh
   ```

2. **Or install manually:**

   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nodejs npm git
   sudo apt install libzbar0 libdmtx0a tesseract-ocr python3-opencv
   ```

   **CentOS/RHEL/Fedora:**
   ```bash
   sudo dnf install python3 python3-pip nodejs npm git
   sudo dnf install zbar-devel libdmtx-devel tesseract opencv-python3
   ```

   **Arch Linux:**
   ```bash
   sudo pacman -S python python-pip nodejs npm git
   sudo pacman -S zbar libdmtx tesseract opencv python-opencv
   ```

### Installation Steps

1. **Run automated setup:**
   ```bash
   python3 setup.py
   ```

2. **Start the application:**
   ```bash
   ./start_cnc_system.sh
   ```

### Linux-Specific Issues

**Serial port permissions:**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Logout and login again
```

**Python3 vs python:**
```bash
# If python3 command not found, create alias
sudo ln -s /usr/bin/python3 /usr/bin/python
```

**Package compilation errors:**
```bash
# Use Linux-specific requirements
pip3 install -r requirements-linux.txt
```

## 🍎 macOS Setup

### Prerequisites

1. **Install Homebrew:**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install dependencies:**
   ```bash
   brew install python node git
   brew install zbar libdmtx tesseract opencv
   ```

### Installation Steps

1. **Run automated setup:**
   ```bash
   python3 setup.py
   ```

2. **Start the application:**
   ```bash
   ./start_cnc_system.sh
   ```

### macOS-Specific Issues

**Xcode Command Line Tools:**
```bash
xcode-select --install
```

**Serial port permissions:**
- Usually no special permissions needed
- Ports appear as /dev/tty.usbserial-*

## 🔧 Platform-Specific Configurations

### Environment Variables

Create `.env` file in `backend-flask/` directory:

**Windows:**
```env
# Windows-specific paths
LOG_FILE=logs\\cnc_app.log
DATABASE_URL=sqlite:///./cnc_database.db
```

**Linux/macOS:**
```env
# Unix-specific paths
LOG_FILE=logs/cnc_app.log
DATABASE_URL=sqlite:///./cnc_database.db
```

### Serial Port Configuration

**Windows:**
- Ports: COM1, COM2, COM3, etc.
- Check Device Manager → Ports (COM & LPT)

**Linux:**
- Ports: /dev/ttyUSB0, /dev/ttyACM0, etc.
- Check: `ls /dev/ttyUSB* /dev/ttyACM*`

**macOS:**
- Ports: /dev/tty.usbserial-*, /dev/cu.usbserial-*
- Check: `ls /dev/tty.*`

## 🐛 Platform-Specific Troubleshooting

### Windows Issues

**Python not in PATH:**
```cmd
# Use full path
C:\\Python311\\python.exe setup.py
```

**npm install fails:**
```cmd
# Clear cache and retry
npm cache clean --force
npm install --legacy-peer-deps
```

**Package compilation errors:**
```cmd
# Install Visual Studio Build Tools
# Or use pre-compiled wheels
pip install --only-binary=all -r requirements-windows.txt
```

### Linux Issues

**Permission denied on serial ports:**
```bash
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER
# Logout and login
```

**Missing system libraries:**
```bash
# Install development packages
sudo apt install build-essential python3-dev
```

**Node.js version too old:**
```bash
# Install newer Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### macOS Issues

**Command Line Tools missing:**
```bash
xcode-select --install
```

**Homebrew permissions:**
```bash
sudo chown -R $(whoami) /usr/local/share/zsh
```

## 📦 Alternative Installation Methods

### Using Conda (Cross-platform)

```bash
# Create conda environment
conda create -n cnc-project python=3.11
conda activate cnc-project

# Install packages
conda install -c conda-forge opencv numpy scipy matplotlib
pip install -r requirements.txt
```

### Using Docker (Cross-platform)

```bash
# Build Docker image
docker build -t cnc-project .

# Run container
docker run -p 8000:8000 -p 5173:5173 cnc-project
```

### Using Virtual Machines

For testing cross-platform compatibility:

1. **VirtualBox/VMware** with different OS images
2. **Windows Subsystem for Linux (WSL)** on Windows
3. **Parallels Desktop** on macOS

## 🔍 Verification Commands

Run these commands to verify your installation:

```bash
# Check Python
python --version
python -c "import sys; print(sys.platform)"

# Check Node.js
node --version
npm --version

# Check Git
git --version

# Check Python packages
python -c "import cv2, numpy, fastapi; print('Core packages OK')"

# Check serial ports
python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
```

## 📞 Platform-Specific Support

### Windows
- [Windows Python Guide](https://docs.python.org/3/using/windows.html)
- [Node.js Windows Guide](https://nodejs.org/en/download/package-manager/#windows)

### Linux
- [Linux Python Guide](https://docs.python.org/3/using/unix.html)
- [Node.js Linux Guide](https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions)

### macOS
- [macOS Python Guide](https://docs.python.org/3/using/mac.html)
- [Node.js macOS Guide](https://nodejs.org/en/download/package-manager/#macos)

## 🎯 Best Practices

1. **Use virtual environments** to avoid conflicts
2. **Keep dependencies updated** but test thoroughly
3. **Use platform-specific requirements** if main file fails
4. **Test on target platform** before deployment
5. **Document platform-specific quirks** for your team

---

**Need help with a specific platform?** Create an issue on GitHub with your OS details and error messages!

