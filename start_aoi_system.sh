#!/bin/bash
echo "================================================"
echo "            AOI Platform Launcher"
echo "         Industrial Vision & Automation"
echo "================================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if this is first-time setup
if [ ! -d "venv" ]; then
    echo "[SETUP] First time setup detected..."
    echo "[SETUP] Running initial configuration..."
    echo
    python3.13 setup.py 2>/dev/null || python3.12 setup.py 2>/dev/null || python3.11 setup.py 2>/dev/null || python3.10 setup.py 2>/dev/null || python3.9 setup.py 2>/dev/null || python3.8 setup.py 2>/dev/null || python3 setup.py || python setup.py
    if [ $? -ne 0 ]; then
        echo "[ERROR] Setup failed! Please check the errors above."
        echo
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo
    echo "[SETUP] Configuration completed successfully!"
    echo
fi

if [ ! -d "aoi-web-front/node_modules" ]; then
    echo "[SETUP] Installing frontend dependencies..."
    echo
    cd aoi-web-front
    npm install
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install frontend dependencies!"
        cd ..
        read -p "Press Enter to exit..."
        exit 1
    fi
    cd ..
    echo "[SETUP] Frontend dependencies installed!"
    echo
fi

echo "[1/2] Starting Backend Server..."
echo "       API will be available at: http://localhost:8000"

# Start backend in background
./start_backend.sh &
BACKEND_PID=$!

echo "[WAIT] Waiting for backend to initialize..."
sleep 5

echo "[2/2] Starting Frontend Server..."
echo "       UI will be available at: http://localhost:5173"

# Start frontend in background
./start_frontend.sh &
FRONTEND_PID=$!

echo
echo "================================================"
echo "            Platform Status"
echo "================================================"
echo "Backend API:   http://localhost:8000"
echo "Frontend UI:   http://localhost:5173"
echo
echo "Both servers are running in the background."
echo "Please wait ~30 seconds for full initialization."
echo
echo "================================================"
echo "To stop the platform:"
echo "   Press Ctrl+C to stop both servers"
echo "================================================"
echo

# Function to handle cleanup
cleanup() {
    echo
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Servers stopped."
    exit 0
}

# Set trap to handle Ctrl+C
trap cleanup SIGINT

# Wait for user input or processes to end
echo "Press Ctrl+C to stop the platform..."
wait
