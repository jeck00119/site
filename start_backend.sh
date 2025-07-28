#!/bin/bash
# Linux shell script to start the backend server
echo "Starting AOI Backend Server on Linux..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed"
    echo "Please install Python 3.8+ using your package manager"
    echo "For Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "For CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "For Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

# Navigate to backend directory
cd "$(dirname "$0")/backend-flask" || exit 1

# Kill any existing processes on port 8000
echo "Checking for existing server processes..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Killing existing processes on port 8000..."
    lsof -Pi :8000 -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Install Linux-specific packages if needed
echo "Installing Linux-specific packages..."
pip install pyudev 2>/dev/null || echo "pyudev installation failed (optional)"

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data/cognex
mkdir -p reports
mkdir -p config_db

# Set permissions for USB device access (may require sudo)
if [ -d "/dev" ]; then
    echo "Note: You may need to add your user to dialout group for USB access:"
    echo "sudo usermod -a -G dialout \$USER"
    echo "Then log out and log back in."
fi

# Set development environment for CORS
export DEVELOPMENT=true

# Start the server
echo "Starting server..."
python main.py