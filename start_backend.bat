@echo off
echo ========================================
echo     AOI Backend Server
echo ========================================
echo.

REM Go to project root
cd /d "%~dp0"

REM Check if venv exists in root
if not exist "venv" (
    echo Virtual environment not found! Running setup...
    echo.
    call python setup.py
    if errorlevel 1 (
        echo Setup failed! Please check the errors above.
        pause
        exit /b 1
    )
    echo.
    echo Setup completed successfully!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment!
    echo Please check if Python and venv are properly installed.
    pause
    exit /b 1
)
echo Virtual environment activated successfully
echo.

REM Change to backend directory
cd backend-flask
echo Starting backend server on http://localhost:8000...
echo.

REM Start the backend server
python main.py
if errorlevel 1 (
    echo.
    echo Backend failed to start!
    echo Please check the errors above.
    pause
    exit /b 1
)
echo.
echo Backend server stopped.
pause
