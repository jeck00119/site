@echo off
REM Windows batch script to start the frontend development server
echo Starting AOI Frontend Development Server on Windows...

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo npm is not installed or not in PATH
    echo Please install Node.js which includes npm
    pause
    exit /b 1
)

REM Navigate to frontend directory
cd /d "%~dp0aoi-web-front"

REM Install dependencies
echo Installing dependencies...
npm install

REM Start development server
echo Starting development server...
npm run dev

pause