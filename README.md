# AOI Platform

A modern AOI (Automated Optical Inspection) platform for industrial automation with multi-module support and real-time monitoring.

## Features

- **Multi-Module Platform**: Camera systems, robots, CNC, profilometer integration
- **Real-time Monitoring**: Live updates from connected industrial modules  
- **Industrial Configurations**: Support for multiple production setups
- **Inspection Analytics**: YOLO detection, OCR, and quality control algorithms
- **Cross-Platform**: Windows and Linux support with automated setup
- **Computer Vision**: OpenCV, pre-trained ML models, fabric.js canvas

## Quick Start

### Prerequisites

- **Python 3.8-3.13** (automatically detected, latest preferred)
- **Node.js 16+** (LTS recommended)
- **Git** (for cloning)

### Installation

1. **Clone and setup**:
```bash
git clone https://github.com/jeck00119/site.git -b AOI-V1
cd site
python setup.py
```

2. **Start the application**:
```bash
# Start entire platform (recommended)
# Windows
start_aoi_system.bat

# Linux/macOS  
./start_aoi_system.sh

# Or start components individually
# Backend only: start_backend.bat/sh
# Frontend only: start_frontend.bat/sh
```

3. **Access**: 
   - Frontend UI: http://localhost:5173
   - Backend API: http://localhost:8000

## Project Structure

```
site/
├── backend-flask/          # FastAPI backend (despite the name)
│   ├── api/               # API routes and endpoints
│   ├── services/          # Business logic and hardware integration
│   ├── config/            # Configuration management
│   ├── security/          # Authentication and security
│   ├── repo/              # Data access layer
│   ├── requirements.txt   # Python dependencies
│   └── main.py           # API entry point
├── aoi-web-front/         # Vue.js 3 + TypeScript frontend
│   ├── src/              # Vue components and store
│   ├── package.json      # Node.js dependencies
│   └── vite.config.ts    # Vite build configuration
├── config_db/             # Product-specific configurations
├── venv/                  # Python virtual environment (auto-created)
├── setup.py              # Cross-platform setup script
└── start_*.bat/sh        # Launch scripts
```

## Configuration

**No manual configuration required!** The platform uses intelligent defaults:

- **Database**: TinyDB (JSON-based, no setup needed)
- **Security**: Auto-generated JWT keys
- **CORS**: Pre-configured for development
- **Python Environment**: Automatically created virtual environment
- **Dependencies**: Auto-installed on first run

## Hardware Integration

The platform supports various industrial hardware:

- **Cameras**: Real-time image capture and processing
- **Robots**: xArm integration for automated handling
- **CNC Controllers**: GRBL and Marlin firmware support with safety controls  
- **Profilometers**: Gocator 3D measurement systems
- **OCR Systems**: Tesseract text recognition (cross-platform)

## Usage

1. **First Time**: Run `python setup.py` - creates environment and installs everything
2. **Launch Platform**: Use `start_aoi_system.bat/sh` for complete system
3. **Configure Hardware**: Connect cameras, robots, and measurement devices
4. **Set Inspection Parameters**: Configure detection algorithms and quality thresholds
5. **Run Inspection**: Execute automated optical inspection workflows

## Development

The platform automatically handles environment setup. For manual development:

**Backend Development**:
```bash
# Activate the auto-created venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate.bat  # Windows

cd backend-flask
python main.py
```

**Frontend Development**:
```bash
cd aoi-web-front
npm run dev
```

## Technology Stack

- **Backend**: Python FastAPI, Pydantic, TinyDB, OpenCV, YOLOv8
- **Frontend**: Vue 3, TypeScript, Vite, CoreUI, Fabric.js
- **Hardware**: Cross-platform driver integration
- **Vision**: Pre-trained ML models, real-time processing

## Troubleshooting

**Setup Issues**:
- **Python not found**: Install Python 3.8-3.13 from python.org
- **Node.js issues**: Install Node.js LTS from nodejs.org
- **Permission errors**: Run as administrator (Windows) or check file permissions

**Runtime Issues**:
- **Backend fails**: Check `venv` exists, run `python setup.py` again
- **Frontend fails**: Delete `node_modules`, run `npm install`
- **Hardware not detected**: Verify USB connections and driver installation

## Scripts Reference

- `setup.py` - Initial setup (creates venv, installs dependencies)
- `start_aoi_system.bat/sh` - Launch complete platform
- `start_backend.bat/sh` - Backend API only
- `start_frontend.bat/sh` - Frontend UI only

## License

MIT License

