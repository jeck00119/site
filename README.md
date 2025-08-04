# 🏭 CNC Control System

A modern, full-stack CNC control system with real-time monitoring, multi-firmware support, and advanced automation features.

## ✨ Features

- 🎛️ **Multi-Firmware Support**: GRBL, FluidNC, and Marlin compatibility
- 🔄 **Real-time Control**: Live position updates and command execution
- 📱 **Responsive UI**: Works on desktop and mobile devices
- 🔒 **Secure**: JWT authentication and input validation
- 🚀 **High Performance**: Optimized for low latency and high throughput
- 🤖 **Automation Ready**: Robot integration and automated workflows

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (recommended: Python 3.11)
- **Node.js 16+** (recommended: Node.js 20)
- **Git** (optional but recommended)

#### Platform-Specific Installation

**Windows:**
- Python: Download from [python.org](https://www.python.org/downloads/)
- Node.js: Download from [nodejs.org](https://nodejs.org/)
- Git: Download from [git-scm.com](https://git-scm.com/)

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm git
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install python3 python3-pip nodejs npm git
```

**macOS:**
```bash
# Using Homebrew
brew install python node git
```

### 1. Clone the Repository

```bash
git clone https://github.com/jeck00119/site.git
cd site
```

### 2. Automated Setup (Recommended)

```bash
# Run the cross-platform setup script
python setup.py
```

The setup script will:
- ✅ Detect your platform (Windows/Linux/macOS)
- ✅ Check all prerequisites
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Generate platform-specific start scripts
- ✅ Create configuration files

### 3. Manual Setup (Alternative)

<details>
<summary>Click to expand manual setup instructions</summary>

#### Backend Setup

```bash
# Navigate to backend directory
cd backend-flask

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (Command Prompt):
venv\Scripts\activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Copy environment configuration
cp ../.env.example .env
```

#### Frontend Setup

```bash
# Open new terminal and navigate to frontend directory
cd aoi-web-front

# Install dependencies
npm install
```

</details>

### 4. Start the Application

#### Option A: Individual Scripts

**Windows:**
```bash
# Start backend (in one terminal)
start_backend.bat
# Or use PowerShell
start_backend.ps1

# Start frontend (in another terminal)
start_frontend.bat
```

**Linux/macOS:**
```bash
# Start backend (in one terminal)
./start_backend.sh

# Start frontend (in another terminal)
./start_frontend.sh
```

#### Option B: Combined Start (Recommended)

**Windows:**
```bash
start_cnc_system.bat
```

**Linux/macOS:**
```bash
./start_cnc_system.sh
```

### 5. Access the Application

Open your browser and go to `http://localhost:5173`

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
site/
├── backend-flask/          # Python FastAPI backend
│   ├── main.py             # Application entry point
│   ├── api/                # API routes and endpoints
│   ├── services/           # Business logic and services
│   ├── config/             # Configuration management
│   └── security/           # Authentication and security
├── aoi-web-front/          # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── store/          # Vuex state management
│   │   └── utils/          # Utility functions
│   └── package.json
├── requirements.txt        # Python dependencies
└── .env.example           # Environment configuration template
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and update the values:

```bash
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Database Configuration
DATABASE_URL=sqlite:///./cnc_database.db

# Security Configuration
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# CORS Configuration
CORS_ORIGINS=["http://localhost:5173"]
```

### CNC Hardware Setup

1. Connect your CNC machine via USB/Serial
2. Configure the appropriate firmware type in the web interface
3. Set the correct baud rate (usually 115200)
4. Test the connection using the terminal interface

## 🎯 Usage

### Basic CNC Control

1. **Connect to CNC**: Select your CNC port and firmware type
2. **Home the Machine**: Use the "Home" command to establish reference points
3. **Manual Control**: Use the directional controls to move axes
4. **Send Commands**: Use the terminal to send G-code commands
5. **Monitor Status**: View real-time position and machine state

### Advanced Features

- **Location Shortcuts**: Save and recall frequently used positions
- **Automated Workflows**: Create and execute complex movement sequences
- **Real-time Monitoring**: Track machine performance and status
- **Multi-machine Support**: Control multiple CNC machines simultaneously

## 🔧 Development

### Backend Development

```bash
cd backend-flask

# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd aoi-web-front

# Install dependencies
npm install

# Start development server with hot reload
npm run dev

# Build for production
npm run build
```

### Code Quality

The project includes:
- **Type Safety**: Pydantic models for data validation
- **Security**: JWT authentication and input sanitization
- **Performance**: Optimized WebSocket communication
- **Testing**: Comprehensive test coverage

## 🐛 Troubleshooting

### Common Issues

#### Platform-Specific Issues

**Windows:**

*Python not found:*
```bash
# Add Python to PATH or use full path
C:\Python311\python.exe setup.py
```

*Virtual environment activation fails:*
```bash
# Try PowerShell instead of Command Prompt
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

*Permission denied errors:*
```bash
# Run as Administrator or use PowerShell
```

**Linux:**

*Python3 not found:*
```bash
# Install Python 3
sudo apt install python3 python3-pip python3-venv
# Or use python instead of python3
python setup.py
```

*Permission denied for serial ports:*
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Logout and login again
```

*Node.js version too old:*
```bash
# Install newer Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### General Issues

**Backend won't start:**
- Check Python version: `python --version`
- Verify virtual environment is activated
- Check port availability: `netstat -an | grep 8000`
- Review error messages in terminal

**Frontend won't start:**
- Check Node.js version: `node --version`
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check port availability: `netstat -an | grep 5173`

**CNC connection issues:**
- Verify USB/Serial connection
- Check device permissions (Linux/macOS): `ls -l /dev/ttyUSB* /dev/ttyACM*`
- Ensure correct baud rate and firmware type
- Try different USB ports
- Check for driver requirements

**WebSocket connection errors:**
- Check firewall settings
- Verify CORS configuration in `.env`
- Ensure backend is running on port 8000
- Try different browser or disable extensions

### Platform-Specific Serial Port Detection

**Windows:**
- Check Device Manager → Ports (COM & LPT)
- Look for COM ports (e.g., COM3, COM4)

**Linux:**
```bash
# List USB serial devices
ls /dev/ttyUSB* /dev/ttyACM*
# Check dmesg for device detection
dmesg | grep tty
```

**macOS:**
```bash
# List serial devices
ls /dev/tty.*
# Check system report
system_profiler SPUSBDataType
```

### Getting Help

1. Check the [INSTALL.md](INSTALL.md) for detailed setup instructions
2. Review error messages carefully
3. Ensure all prerequisites are installed correctly
4. Verify your hardware connections
5. Create an issue on GitHub with:
   - Operating system and version
   - Python and Node.js versions
   - Complete error messages
   - Steps to reproduce the issue

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.15, or Linux (Ubuntu 18.04+)
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Python**: 3.8+
- **Node.js**: 16+

### Recommended Requirements
- **OS**: Windows 11, macOS 12+, or Linux (Ubuntu 20.04+)
- **RAM**: 8GB+
- **Storage**: 5GB+ free space
- **Python**: 3.11
- **Node.js**: 20+

## 🔒 Security

- JWT-based authentication
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure WebSocket connections
- Environment-based configuration

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

---

**Happy CNC Controlling!** 🎛️✨

