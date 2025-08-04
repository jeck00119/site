# 📦 Installation Guide

This guide provides detailed installation instructions for the CNC Control System.

## 🚀 Automated Setup (Recommended)

The easiest way to set up the project is using the automated setup script:

```bash
# Clone the repository
git clone https://github.com/jeck00119/site.git
cd site

# Run the setup script
python setup.py
```

The script will:
- ✅ Check prerequisites (Python 3.8+, Node.js 16+)
- ✅ Create Python virtual environment
- ✅ Install all backend dependencies
- ✅ Install all frontend dependencies
- ✅ Create environment configuration
- ✅ Generate start scripts

## 🔧 Manual Setup

If you prefer manual installation or the automated script fails:

### 1. Prerequisites

**Python 3.8+**
```bash
# Check Python version
python --version

# If Python is not installed, download from:
# https://www.python.org/downloads/
```

**Node.js 16+**
```bash
# Check Node.js version
node --version

# If Node.js is not installed, download from:
# https://nodejs.org/
```

**Git**
```bash
# Check Git version
git --version

# If Git is not installed, download from:
# https://git-scm.com/
```

### 2. Clone Repository

```bash
git clone https://github.com/jeck00119/site.git
cd site
```

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend-flask

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r ../requirements.txt

# Copy environment configuration
cp ../.env.example .env

# Edit .env file with your settings (optional)
# nano .env  # or use your preferred editor
```

### 4. Frontend Setup

```bash
# Open new terminal and navigate to frontend directory
cd aoi-web-front

# Install dependencies
npm install

# Optional: Update dependencies
# npm update
```

### 5. Database Setup

The application uses SQLite by default, which requires no additional setup. The database file will be created automatically when you first run the backend.

For production environments, you can configure PostgreSQL or MySQL by updating the `DATABASE_URL` in your `.env` file.

## 🏃‍♂️ Running the Application

### Option 1: Using Start Scripts (After Automated Setup)

**Windows:**
```bash
# Start backend (in one terminal)
start_backend.bat

# Start frontend (in another terminal)
start_frontend.bat
```

**macOS/Linux:**
```bash
# Start backend (in one terminal)
./start_backend.sh

# Start frontend (in another terminal)
./start_frontend.sh
```

### Option 2: Manual Start

**Backend:**
```bash
cd backend-flask

# Activate virtual environment
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate

# Start the server
python main.py
```

**Frontend:**
```bash
cd aoi-web-front

# Start development server
npm run dev
```

### 6. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

Edit the `.env` file in the `backend-flask` directory:

```bash
# Server Configuration
SERVER_HOST=0.0.0.0          # Server host (0.0.0.0 for all interfaces)
SERVER_PORT=8000             # Server port
DEBUG=True                   # Enable debug mode

# Database Configuration
DATABASE_URL=sqlite:///./cnc_database.db  # Database connection string

# Security Configuration
SECRET_KEY=your-secret-key-here           # Change this in production
JWT_SECRET_KEY=your-jwt-secret-key-here   # Change this in production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/cnc_app.log
```

### Hardware Configuration

For CNC hardware setup:

1. **Connect CNC Machine**: Connect via USB/Serial port
2. **Check Device**: Verify the device appears in your system
   - Windows: Device Manager → Ports (COM & LPT)
   - macOS: `ls /dev/tty.*`
   - Linux: `ls /dev/ttyUSB* /dev/ttyACM*`
3. **Configure Firmware**: Set the correct firmware type (GRBL, FluidNC, Marlin)
4. **Set Baud Rate**: Usually 115200 for most CNC controllers

## 🐛 Troubleshooting

### Common Installation Issues

**Python Virtual Environment Issues:**
```bash
# If venv creation fails, try:
python3 -m venv venv

# Or use virtualenv:
pip install virtualenv
virtualenv venv
```

**Permission Issues (Linux/macOS):**
```bash
# If you get permission errors:
sudo chown -R $USER:$USER /path/to/project
chmod +x start_backend.sh start_frontend.sh
```

**Node.js Issues:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Port Already in Use:**
```bash
# Check what's using port 8000
netstat -an | grep 8000

# Kill process using port (replace PID)
kill -9 <PID>
```

### Hardware Issues

**CNC Not Detected:**
- Check USB cable connection
- Try different USB port
- Install USB drivers if needed
- Check device permissions (Linux/macOS)

**Connection Timeout:**
- Verify baud rate settings
- Check firmware type selection
- Ensure CNC is powered on
- Try different serial settings

### Performance Issues

**Slow Response:**
- Check system resources (CPU, RAM)
- Close unnecessary applications
- Verify network connectivity
- Check for antivirus interference

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.15, Ubuntu 18.04
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Python**: 3.8+
- **Node.js**: 16+

### Recommended Requirements
- **OS**: Windows 11, macOS 12+, Ubuntu 20.04+
- **RAM**: 8GB+
- **Storage**: 5GB+ free space
- **Python**: 3.11
- **Node.js**: 20+

## 🔄 Updates

To update the project:

```bash
# Pull latest changes
git pull origin master

# Update backend dependencies
cd backend-flask
source venv/bin/activate  # or venv\\Scripts\\activate on Windows
pip install -r ../requirements.txt

# Update frontend dependencies
cd ../aoi-web-front
npm install
```

## 🆘 Getting Help

If you encounter issues:

1. **Check this guide** for common solutions
2. **Review error messages** carefully
3. **Check system requirements** are met
4. **Verify hardware connections**
5. **Create an issue** on GitHub with:
   - Operating system and version
   - Python and Node.js versions
   - Complete error messages
   - Steps to reproduce the issue

## 📞 Support

- **GitHub Issues**: https://github.com/jeck00119/site/issues
- **Documentation**: Check the README.md file
- **Community**: Join discussions in GitHub Discussions

---

**Need help?** Don't hesitate to create an issue on GitHub! 🤝

