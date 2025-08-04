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
- **Node.js 18+** (recommended: Node.js 20)
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/jeck00119/site.git
cd site
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend-flask

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Copy environment configuration
cp ../.env.example .env

# Start the backend server
python main.py
```

The backend will start on `http://localhost:8000`

### 3. Frontend Setup

```bash
# Open new terminal and navigate to frontend directory
cd aoi-web-front

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start on `http://localhost:5173`

### 4. Access the Application

Open your browser and go to `http://localhost:5173`

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

**Backend won't start:**
- Check Python version: `python --version`
- Verify all dependencies: `pip list`
- Check port availability: `netstat -an | grep 8000`

**Frontend won't start:**
- Check Node.js version: `node --version`
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

**CNC connection issues:**
- Verify USB/Serial connection
- Check device permissions (Linux/macOS)
- Ensure correct baud rate and firmware type
- Try different USB ports

**WebSocket connection errors:**
- Check firewall settings
- Verify CORS configuration
- Ensure backend is running on port 8000

### Getting Help

1. Check the [Issues](https://github.com/jeck00119/site/issues) page
2. Review the troubleshooting section above
3. Ensure all prerequisites are installed correctly
4. Verify your hardware connections

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

