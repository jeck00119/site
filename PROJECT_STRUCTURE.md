# AOI (Automated Optical Inspection) System - Project Structure

## Project Overview
This is an industrial vision inspection system for automated optical inspection (AOI) of PCB boards and electronic components. The system integrates computer vision, machine learning, CNC control, and robot automation.

## Technology Stack

### Backend (FastAPI/Python)
- **Framework**: FastAPI with Uvicorn ASGI server
- **Computer Vision**: OpenCV, PIL, scikit-image
- **Machine Learning**: PyTorch, Ultralytics (YOLO), Segment Anything, EasyOCR
- **Database**: TinyDB (JSON-based)
- **Authentication**: JWT with passlib/bcrypt
- **Hardware Control**: PySerial (CNC), pymycobot/xarm (robots)
- **WebSocket**: Native FastAPI WebSocket support
- **Platform Support**: Windows (primary) and Linux

### Frontend (Vue 3)
- **Framework**: Vue 3 with Composition API
- **State Management**: Vuex 4
- **Router**: Vue Router 4
- **UI Components**: CoreUI Vue, Fabric.js (canvas), Vue3 Context Menu
- **Build Tool**: Vite
- **TypeScript**: Full TypeScript support
- **Styling**: CSS with design tokens

## Architecture

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Vue 3)                     │
│  - Single Page Application                                   │
│  - Real-time WebSocket connections                          │
│  - Canvas-based image annotation                            │
└─────────────────────────────────────────────────────────────┘
                               │
                               │ HTTP/WebSocket
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  - RESTful API endpoints                                     │
│  - WebSocket connections for real-time updates              │
│  - Service-oriented architecture                            │
│  - Security middleware (CSRF, Rate limiting)                │
└─────────────────────────────────────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌────────────┐ ┌────────────┐ ┌────────────┐
        │  TinyDB    │ │  Hardware  │ │   Vision   │
        │  Storage   │ │  Control   │ │ Processing │
        └────────────┘ └────────────┘ └────────────┘
```

## Directory Structure

### Root Level
```
site/
├── aoi-web-front/          # Vue.js frontend application
├── backend-flask/          # FastAPI backend (despite the name)
├── config_db/              # Configuration database files
├── start_*.bat/sh          # System startup scripts
└── requirements.txt        # Python dependencies
```

### Backend Structure (`backend-flask/`)
```
backend-flask/
├── main.py                 # FastAPI application entry point
├── config/                 # Centralized configuration
│   ├── manager.py         # Configuration manager
│   ├── settings.py        # Application settings
│   ├── database.py        # Database configuration
│   ├── hardware.py        # Hardware settings
│   ├── security.py        # Security configuration
│   └── server.py          # Server configuration
│
├── api/
│   ├── routers/           # API route handlers (26 modules)
│   │   ├── algorithm_routes.py
│   │   ├── camera_routes.py
│   │   ├── cnc_routes.py
│   │   ├── components_routes.py
│   │   ├── authentication_routes.py
│   │   └── ... (20+ more route modules)
│   ├── ws_connection_manager.py  # WebSocket manager
│   └── error_handlers.py         # Global error handling
│
├── services/              # Business logic layer
│   ├── service_manager.py        # Service orchestrator
│   ├── algorithms/               # Vision algorithms
│   │   ├── algorithms_service.py
│   │   ├── algorithms_factory.py
│   │   └── models/              # Algorithm models
│   ├── camera/                  # Camera management
│   ├── cnc/                     # CNC machine control
│   ├── robot/                   # Robot arm control
│   ├── authentication/          # Auth service
│   ├── processing/              # Image processing
│   └── ... (15+ service modules)
│
├── repo/                  # Data access layer
│   ├── abstract_repo.py         # Base repository
│   └── repositories.py          # Specific repositories
│
├── security/              # Security infrastructure
│   ├── middleware.py            # Security middleware
│   ├── auth.py                  # Authentication
│   ├── encryption.py            # Encryption utilities
│   └── validators.py            # Input validation
│
├── config_db/             # Per-configuration databases
│   ├── IBS-*/                   # Product-specific configs
│   └── configurations.json      # Master configuration
│
└── assets/                # Static assets
    ├── mobile_sam/              # SAM model files
    └── yolov8/                  # YOLO model files
```

### Frontend Structure (`aoi-web-front/`)
```
aoi-web-front/
├── src/
│   ├── main.js                  # Vue app entry
│   ├── router.js                # Route definitions
│   ├── App.vue                  # Root component
│   │
│   ├── components/
│   │   ├── base/                # Reusable UI components
│   │   │   ├── BaseButton.vue
│   │   │   ├── BaseDialog.vue
│   │   │   └── ... (15+ components)
│   │   ├── pages/               # Page components
│   │   │   ├── home/
│   │   │   ├── auth/
│   │   │   ├── inspections/
│   │   │   ├── settings/
│   │   │   └── tools/
│   │   ├── cnc/                 # CNC control components
│   │   ├── camera/              # Camera components
│   │   └── layout/              # Layout components
│   │
│   ├── store/                   # Vuex state management
│   │   ├── index.js             # Store configuration
│   │   └── modules/             # Store modules (20+)
│   │       ├── algorithms/
│   │       ├── camera_settings/
│   │       ├── cnc/
│   │       ├── components/
│   │       └── ... (each with actions, getters, mutations)
│   │
│   ├── utils/                   # Utility functions
│   │   ├── api.ts              # API client
│   │   ├── requests.ts         # HTTP requests
│   │   └── validation.js       # Form validation
│   │
│   └── types/                   # TypeScript definitions
│       ├── api.ts
│       └── store.ts
│
├── public/                      # Static assets
├── package.json                 # NPM dependencies
└── vite.config.ts              # Vite configuration
```

## Core Features & Modules

### 1. Vision & Inspection
- **Algorithms**: Multiple computer vision algorithms for defect detection
- **Components**: PCB component inspection and validation
- **References**: Reference image management for comparison
- **Custom Components**: User-defined component types
- **Identifications**: Barcode/QR code reading, OCR

### 2. Hardware Control
- **CNC Control**: GRBL/Marlin firmware support for positioning
- **Robot Arms**: MyCobot and xArm robot integration
- **Camera Management**: Multi-camera support with calibration
- **Profilometer**: 3D surface measurement integration

### 3. Process Management
- **Inspection Lists**: Batch inspection management
- **Process Service**: Inspection workflow orchestration
- **Image Sources**: Multiple image input sources
- **Image Generators**: Synthetic image generation

### 4. Configuration & Data
- **Multi-Configuration**: Support for multiple product configurations
- **TinyDB Storage**: JSON-based persistent storage
- **ITAC Integration**: Manufacturing execution system integration
- **Logging**: Comprehensive application logging

### 5. User Interface
- **Real-time Updates**: WebSocket-based live updates
- **Canvas Annotation**: Fabric.js-based image annotation
- **Responsive Design**: Adaptive UI for different screens
- **Multi-language**: Internationalization support

## API Structure

### Main API Endpoints

#### Vision & Inspection
- `/api/algorithms` - Algorithm management and execution
- `/api/components` - Component configuration
- `/api/references` - Reference image management
- `/api/identifications` - Identification algorithms
- `/api/masks` - Image masking operations

#### Hardware Control
- `/api/cnc` - CNC machine control
- `/api/robot` - Robot arm control
- `/api/camera` - Camera management
- `/api/camera-settings` - Camera configuration
- `/api/profilometer` - Profilometer control

#### Process Management
- `/api/process` - Inspection process control
- `/api/inspection-list` - Batch inspection management
- `/api/image-source` - Image source configuration

#### System Configuration
- `/api/configurations` - System configurations
- `/api/authentication` - User authentication
- `/api/media` - Audio/visual feedback
- `/api/log` - Application logging

### WebSocket Endpoints
- `/ws/cnc/{cnc_uid}` - Real-time CNC status
- `/ws/process` - Inspection process updates
- `/ws/camera` - Live camera feed

## Data Models (Pydantic)

### Core Models
- `CncModel` - CNC machine configuration
- `LocationModel` - CNC position locations
- `ComponentModel` - Component definitions
- `ReferenceModel` - Reference image data
- `AlgorithmModel` - Algorithm configurations
- `InspectionModel` - Inspection results
- `UserModel` - User authentication

## Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (Admin, Operator, Viewer)
- Secure password hashing (bcrypt)

### Middleware
- CSRF protection
- Rate limiting
- Security headers
- Input validation

## Development & Deployment

### Development Mode
```bash
# Backend
cd backend-flask
python main.py

# Frontend
cd aoi-web-front
npm run dev
```

### Production Build
```bash
# Frontend build
cd aoi-web-front
npm run build

# Start system
./start_aoi_system.bat  # Windows
./start_aoi_system.sh   # Linux
```

### Configuration Files
- Backend: `config/settings.py` - Application settings
- Frontend: `vite.config.ts` - Build configuration
- Database: `config_db/configurations.json` - Product configs

## Key Technical Decisions

1. **FastAPI over Flask**: Despite the directory name, uses FastAPI for async support
2. **TinyDB**: Lightweight JSON database for configuration storage
3. **Service Architecture**: Clean separation of concerns with service layer
4. **WebSocket Integration**: Real-time updates for hardware status
5. **Platform Abstraction**: Cross-platform support (Windows/Linux)
6. **Modular Design**: Pluggable algorithm and hardware modules

## Integration Points

### External Systems
- ITAC MES integration
- Basler camera SDK (pypylon)
- Robot arm SDKs (pymycobot, xarm)
- CNC firmware (GRBL, Marlin)

### AI/ML Models
- YOLOv8 for object detection
- Segment Anything (SAM) for segmentation
- EasyOCR for text recognition
- Custom PyTorch models

## Performance Considerations

- Async/await for non-blocking operations
- WebSocket for real-time communication
- Image caching and optimization
- Lazy loading in frontend
- Connection pooling for hardware

## Future Extensibility

The architecture supports:
- Adding new vision algorithms
- Integrating additional hardware
- Extending API endpoints
- Custom UI components
- Plugin-based extensions