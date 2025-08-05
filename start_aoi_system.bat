@echo off
echo Starting Complete AOI Platform...
echo.
echo Starting Backend...
start "AOI Backend" cmd /k "%~dp0start_backend.bat"
timeout /t 3 /nobreak > nul
echo Starting Frontend...
start "AOI Frontend" cmd /k "%~dp0start_frontend.bat"
echo.
echo Both servers are starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:5173
echo.
pause
