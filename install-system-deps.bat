@echo off
REM System dependencies installer for Windows
REM Run this script as Administrator if needed

echo 🔧 Installing system dependencies for CNC Project on Windows...
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ⚠️  Not running as Administrator - some installations may fail
    echo    Right-click and "Run as Administrator" if you encounter issues
)

echo.
echo 📋 This script will guide you through installing required dependencies:
echo.
echo 1. Python 3.8+ (if not already installed)
echo 2. Node.js 16+ (if not already installed)
echo 3. Git (optional but recommended)
echo 4. Visual C++ Build Tools (for some Python packages)
echo.

REM Check Python
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Python is already installed
    python --version
) else (
    echo ❌ Python not found
    echo.
    echo 📥 Please download and install Python from:
    echo    https://www.python.org/downloads/
    echo.
    echo ⚠️  Important: Check "Add Python to PATH" during installation
    echo.
    pause
)

REM Check Node.js
node --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Node.js is already installed
    node --version
) else (
    echo ❌ Node.js not found
    echo.
    echo 📥 Please download and install Node.js from:
    echo    https://nodejs.org/
    echo.
    echo 💡 Choose the LTS version for best compatibility
    echo.
    pause
)

REM Check Git
git --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Git is already installed
    git --version
) else (
    echo ⚠️  Git not found (optional but recommended)
    echo.
    echo 📥 You can download Git from:
    echo    https://git-scm.com/download/win
    echo.
)

REM Check Visual C++ Build Tools
echo.
echo 🔍 Checking for Visual C++ Build Tools...
where cl >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Visual C++ Build Tools found
) else (
    echo ⚠️  Visual C++ Build Tools not found
    echo.
    echo 📥 Some Python packages may require Visual C++ Build Tools.
    echo    If you encounter compilation errors, install from:
    echo    https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo.
    echo 💡 Or install Visual Studio Community with C++ workload
    echo.
)

REM Check Windows SDK (for some packages)
echo.
echo 🔍 Checking for Windows SDK...
if exist "C:\Program Files (x86)\Windows Kits\10" (
    echo ✅ Windows SDK found
) else (
    echo ⚠️  Windows SDK not found
    echo    This may be needed for some advanced packages
)

echo.
echo 📦 Installing/Upgrading Python packages...
echo.

REM Upgrade pip
python -m pip install --upgrade pip
if %errorLevel% neq 0 (
    echo ❌ Failed to upgrade pip
    echo    Try running as Administrator
    pause
)

REM Install wheel and setuptools
python -m pip install --upgrade wheel setuptools
if %errorLevel% neq 0 (
    echo ⚠️  Warning: Could not install wheel/setuptools
)

echo.
echo 🎉 Windows system dependencies check complete!
echo.
echo 📋 Next steps:
echo 1. If any dependencies were missing, install them and run this script again
echo 2. Run: python setup.py
echo 3. Or manually install Python packages: pip install -r requirements.txt
echo.
echo 💡 If you encounter issues with specific packages, try:
echo    pip install -r requirements-windows.txt
echo.
echo 🔧 Common Windows-specific solutions:
echo    - Use requirements-windows.txt for problematic packages
echo    - Install Visual Studio Community for C++ compilation
echo    - Use conda instead of pip for scientific packages
echo    - Install packages from wheel files if available
echo.

pause

