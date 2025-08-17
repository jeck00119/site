@echo off
echo ========================================
echo     AOI Frontend Server
echo ========================================
echo.

REM Change to frontend directory
cd /d "%~dp0aoi-web-front"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Node modules not found! Installing dependencies...
    echo.
    npm install
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
if errorlevel 1 (
    echo.
    echo Frontend failed to start!
    echo Please check the errors above.
    pause
    exit /b 1
)
echo.
echo Frontend server stopped.
pause
