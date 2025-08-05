# AOI Platform

A modern AOI (Automated Optical Inspection) platform for industrial automation with multi-module support and real-time monitoring.

## Features

- **Multi-Module Platform**: Camera systems, robots, CNC, profilometer
- **Real-time Monitoring**: Live updates from connected industrial modules  
- **Industrial Configurations**: Support for multiple production setups
- **Inspection Analytics**: Detection and quality control algorithms

## Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**

### Installation

1. **Clone and setup**:
```bash
git clone https://github.com/jeck00119/site.git
cd site
python setup.py
```

2. **Start the application**:
```bash
# Windows
start_aoi_system.bat

# Linux/macOS  
./start_aoi_system.sh
```

3. **Access**: Open http://localhost:5173

## Project Structure

```
site/
├── backend-flask/          # Python FastAPI backend
├── aoi-web-front/          # Vue.js frontend
├── requirements.txt        # Python dependencies
└── .env.example           # Environment configuration
```

## Configuration

Copy `.env.example` to `.env` and update:

```bash
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DATABASE_URL=sqlite:///./aoi_database.db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:5173"]
```

## Usage

1. Select your part number configuration
2. Configure cameras and hardware modules
3. Set up inspection algorithms
4. Run automated inspection workflows

## Development

**Backend**:
```bash
cd backend-flask
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend**:
```bash
cd aoi-web-front
npm install
npm run dev
```

## Troubleshooting

**Common Issues**:
- Backend won't start: Check Python version and virtual environment
- Frontend won't start: Check Node.js version, clear npm cache
- Hardware issues: Verify connections and device permissions

## License

MIT License

