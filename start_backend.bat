@echo off
REM Windows batch script to start the backend server
echo Starting AOI Backend Server on Windows...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

REM Navigate to backend directory
cd /d "%~dp0backend-flask"

REM Kill any existing Python processes on port 8000
echo Checking for existing server processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Killing existing process %%a...
    taskkill /F /PID %%a >nul 2>&1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Set development environment for CORS
set DEVELOPMENT=true

REM Start the server
echo Starting server...
python main.py

pause