#!/bin/bash
# Linux shell script to start the frontend development server
echo "Starting AOI Frontend Development Server on Linux..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed"
    echo "Please install Node.js 16+ using your package manager or from https://nodejs.org/"
    echo "For Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
    echo "For CentOS/RHEL: curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - && sudo yum install -y nodejs"
    echo "For Fedora: sudo dnf install nodejs npm"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "npm is not installed"
    echo "Please install Node.js which includes npm"
    exit 1
fi

# Navigate to frontend directory
cd "$(dirname "$0")/aoi-web-front" || exit 1

# Install dependencies
echo "Installing dependencies..."
npm install

# Start development server
echo "Starting development server..."
npm run dev