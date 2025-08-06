#!/bin/bash
echo "========================================"
echo "     AOI Frontend Server"
echo "========================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Change to frontend directory
cd aoi-web-front

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Node modules not found! Installing dependencies..."
    echo
    npm install
    if [ $? -ne 0 ]; then
        echo "Failed to install node modules!"
        echo "Please ensure Node.js and npm are properly installed."
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo
    echo "Dependencies installed successfully!"
    echo
fi

# Start the development server
echo "Starting frontend development server on http://localhost:5173..."
echo
echo "Press Ctrl+C to stop the server"
echo

npm run dev
if [ $? -ne 0 ]; then
    echo
    echo "Frontend failed to start!"
    echo "Please check the errors above."
    read -p "Press Enter to exit..."
    exit 1
fi

echo
echo "Frontend server stopped."
read -p "Press Enter to exit..."
