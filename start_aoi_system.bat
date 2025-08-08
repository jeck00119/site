@echo off
title AOI Platform Launcher
echo ================================================
echo            AOI Platform Launcher
echo         Industrial Vision & Automation
echo ================================================
echo.

REM Check if this is first-time setup
if not exist "venv" (
    echo [SETUP] First time setup detected...
    echo [SETUP] Running initial configuration...
    echo.
    call python setup.py
    if errorlevel 1 (
        echo [ERROR] Setup failed! Please check the errors above.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [SETUP] Configuration completed successfully!
    echo.
)

if not exist "aoi-web-front\node_modules" (
    echo [SETUP] Installing frontend dependencies...
    echo.
    cd aoi-web-front
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies!
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo [SETUP] Frontend dependencies installed!
    echo.
)

echo [1/2] Starting Backend Server...
echo       API will be available at: http://localhost:8000
start "AOI Backend" cmd /k "%~dp0start_backend.bat"

echo [WAIT] Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo [2/2] Starting Frontend Server...
echo       UI will be available at: http://localhost:5173
start "AOI Frontend" cmd /k "%~dp0start_frontend.bat"

echo.
echo ================================================
echo            Platform Status
echo ================================================
echo Backend API:   http://localhost:8000
echo Frontend UI:   http://localhost:5173
echo.
echo Both servers are starting in separate windows.
echo Please wait ~30 seconds for full initialization.
echo.
echo ================================================
echo To stop the platform:
echo   1. Close both server windows
echo   2. Or press Ctrl+C in each window
echo ================================================
echo.
echo Press any key to close this launcher...
pause > nul
