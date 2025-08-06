#!/bin/bash
echo "========================================"
echo "     AOI Backend Server"
echo "========================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if venv exists in root
if [ ! -d "venv" ]; then
    echo "Virtual environment not found! Running setup..."
    echo
    python3.13 setup.py 2>/dev/null || python3.12 setup.py 2>/dev/null || python3.11 setup.py 2>/dev/null || python3.10 setup.py 2>/dev/null || python3.9 setup.py 2>/dev/null || python3.8 setup.py 2>/dev/null || python3 setup.py || python setup.py
    if [ $? -ne 0 ]; then
        echo "Setup failed! Please check the errors above."
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo
    echo "Setup completed successfully!"
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment!"
    echo "Please check if Python and venv are properly installed."
    read -p "Press Enter to exit..."
    exit 1
fi
echo "Virtual environment activated successfully"
echo

# Change to backend directory
cd backend-flask
echo "Starting backend server on http://localhost:8000..."
echo

# Start the backend server
python main.py
if [ $? -ne 0 ]; then
    echo
    echo "Backend failed to start!"
    echo "Please check the errors above."
    read -p "Press Enter to exit..."
    exit 1
fi

echo
echo "Backend server stopped."
read -p "Press Enter to exit..."
