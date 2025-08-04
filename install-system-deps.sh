#!/bin/bash
# System dependencies installer for Linux
# Run this script before installing Python packages

echo "🔧 Installing system dependencies for CNC Project..."

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "Cannot detect Linux distribution"
    exit 1
fi

echo "Detected: $OS $VER"

# Function to install packages based on distribution
install_packages() {
    case "$OS" in
        *"Ubuntu"*|*"Debian"*)
            echo "📦 Installing packages for Ubuntu/Debian..."
            sudo apt-get update
            sudo apt-get install -y \
                python3-dev \
                python3-pip \
                python3-venv \
                build-essential \
                cmake \
                pkg-config \
                libzbar0 \
                libzbar-dev \
                libdmtx0a \
                libdmtx-dev \
                tesseract-ocr \
                tesseract-ocr-eng \
                libqt5gui5 \
                libqt5core5a \
                libqt5widgets5 \
                python3-pyqt5 \
                libopencv-dev \
                python3-opencv \
                libjpeg-dev \
                libpng-dev \
                libtiff-dev \
                libavcodec-dev \
                libavformat-dev \
                libswscale-dev \
                libv4l-dev \
                libxvidcore-dev \
                libx264-dev \
                libgtk-3-dev \
                libatlas-base-dev \
                gfortran \
                nodejs \
                npm
            ;;
        *"CentOS"*|*"Red Hat"*|*"Fedora"*)
            echo "📦 Installing packages for CentOS/RHEL/Fedora..."
            if command -v dnf &> /dev/null; then
                PKG_MGR="dnf"
            else
                PKG_MGR="yum"
            fi
            
            sudo $PKG_MGR install -y \
                python3-devel \
                python3-pip \
                gcc \
                gcc-c++ \
                cmake \
                pkgconfig \
                zbar-devel \
                libdmtx-devel \
                tesseract \
                tesseract-langpack-eng \
                qt5-qtbase-devel \
                opencv-devel \
                python3-opencv \
                libjpeg-turbo-devel \
                libpng-devel \
                libtiff-devel \
                nodejs \
                npm
            ;;
        *"Arch"*)
            echo "📦 Installing packages for Arch Linux..."
            sudo pacman -Syu --noconfirm \
                python \
                python-pip \
                base-devel \
                cmake \
                pkgconf \
                zbar \
                libdmtx \
                tesseract \
                tesseract-data-eng \
                qt5-base \
                opencv \
                python-opencv \
                libjpeg-turbo \
                libpng \
                libtiff \
                nodejs \
                npm
            ;;
        *)
            echo "⚠️  Unsupported distribution: $OS"
            echo "Please install the following packages manually:"
            echo "- Python 3 development headers"
            echo "- Build tools (gcc, cmake)"
            echo "- zbar library and development headers"
            echo "- libdmtx library and development headers"
            echo "- Tesseract OCR"
            echo "- Qt5 development libraries"
            echo "- OpenCV development libraries"
            echo "- Node.js and npm"
            exit 1
            ;;
    esac
}

# Install packages
install_packages

# Verify installations
echo "🔍 Verifying installations..."

# Check Python
if python3 --version &> /dev/null; then
    echo "✅ Python 3: $(python3 --version)"
else
    echo "❌ Python 3 not found"
fi

# Check pip
if python3 -m pip --version &> /dev/null; then
    echo "✅ pip: $(python3 -m pip --version)"
else
    echo "❌ pip not found"
fi

# Check Node.js
if node --version &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
else
    echo "❌ Node.js not found"
fi

# Check npm
if npm --version &> /dev/null; then
    echo "✅ npm: $(npm --version)"
else
    echo "❌ npm not found"
fi

# Check libraries
echo "🔍 Checking system libraries..."
ldconfig -p | grep -q libzbar && echo "✅ libzbar found" || echo "⚠️  libzbar not found"
ldconfig -p | grep -q libdmtx && echo "✅ libdmtx found" || echo "⚠️  libdmtx not found"
which tesseract &> /dev/null && echo "✅ tesseract found" || echo "⚠️  tesseract not found"

echo ""
echo "🎉 System dependencies installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Run: python3 setup.py"
echo "2. Or manually install Python packages: pip3 install -r requirements.txt"
echo ""
echo "💡 If you encounter issues, try using requirements-linux.txt instead:"
echo "   pip3 install -r requirements-linux.txt"

