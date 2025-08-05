@echo off
echo Starting AOI Backend Server...
cd /d "%~dp0backend-flask"
if not exist "venv" (
    echo Virtual environment not found! Please run setup.py first.
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment!
    pause
    exit /b 1
)
echo Virtual environment activated
python main.py
if errorlevel 1 (
    echo Backend failed to start!
    pause
    exit /b 1
)
pause
