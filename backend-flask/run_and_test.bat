@echo off
echo Starting AOI Backend Server for Testing...
echo.

REM Start the backend server in a new window
start "AOI Backend" cmd /c "cd /d %~dp0 && venv\Scripts\python.exe main.py"

REM Wait for server to start
echo Waiting for server to start...
timeout /t 10 /nobreak > nul

REM Run the tests
echo.
echo Running route tests...
echo.
venv\Scripts\python.exe test_routes.py

REM Ask user to close server
echo.
echo Press any key to close the backend server...
pause > nul

REM Kill the backend server
taskkill /FI "WINDOWTITLE eq AOI Backend*" /F > nul 2>&1

echo.
echo Test complete!
pause