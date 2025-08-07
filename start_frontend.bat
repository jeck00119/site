@echo off
echo ========================================
echo     AOI Frontend Server
echo ========================================
echo.

REM Change to frontend directory
cd /d "%~dp0\aoi-web-front"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Node modules not found! Installing dependencies...
    echo.
    call npm install
    if errorlevel 1 (
        echo Failed to install node modules!
        echo Please ensure Node.js and npm are properly installed.
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
)

REM Start the development server
echo Starting frontend development server on http://localhost:5173...
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev
REM Don't check errorlevel for npm run dev since Ctrl+C is normal termination
REM The dev server runs until stopped by user
echo.
echo Frontend server stopped.
pause
