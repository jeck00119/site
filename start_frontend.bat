@echo off
echo Starting AOI Frontend Server...
cd /d "%~dp0aoi-web-front"
if not exist "node_modules" (
    echo Node modules not found! Please run setup.py first.
    pause
    exit /b 1
)
echo Starting development server...
npm run dev
if errorlevel 1 (
    echo Frontend failed to start!
    pause
    exit /b 1
)
pause
