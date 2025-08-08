import sys
import os
import subprocess
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.routers import camera_routes, camera_settings_routes, image_source_routes, components_routes, \
    references_routes, identifications_routes, algorithm_routes, cnc_routes, locations_routes, \
    custom_components_routes, itac_routes, robot_routes, profilometer_routes, inspection_list_routes, process_routes, \
    configuration_routes, media_routes, authentication_routes, log_routes, mask_routes, help_routes, peripheral_routes, \
    camera_calibration_routes, stereo_callibration_routes, annotation_routes
from api.routers import image_generator_routes  
from services.service_manager import ServiceManager
from services.logger.logger_model import AppEntry

# Platform-specific setup
from src.platform_utils import PlatformSpecificConfig, get_platform
PlatformSpecificConfig.setup_environment()

# Centralized Configuration System
from config.manager import get_config_manager
from config.settings import get_settings

# Security System
from security.middleware import SecurityMiddleware, RateLimitMiddleware, CSRFMiddleware

print(f"  Running on {get_platform()}")

# Initialize configuration manager
config_manager = get_config_manager()
settings = get_settings()

def kill_existing_processes(port: int):
    """Kill any existing processes using the specified port"""
    try:
        from src.platform_utils import CommandExecutor
        
        success = CommandExecutor.kill_process_on_port(port)
        if success:
            print(f" Killed existing process on port {port}")
        else:
            print(f"  No process found on port {port} or unable to kill")
                
    except Exception as e:
        print(f"  Could not check/kill existing processes: {e}")

def log_app_event(event_type: str, title: str, description: str, details: str = ""):
    """Log application events using the existing AppLogger service"""
    try:
        app_logger = ServiceManager.app_log
        if app_logger:
            entry = AppEntry(
                timestamp=datetime.now().isoformat(),
                user="system",
                type=event_type,
                title=title,
                description=description,
                details=details
            )
            app_logger.add(entry)
    except Exception:
        # Fallback to console if logging fails
        print(f"[{event_type}] {title}: {description}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    print(" Starting Industrial Vision Application...")
    
    try:
        # Initialize configuration manager
        config_manager.initialize()
        print(" Configuration system initialized")
        
        # Initialize services
        ServiceManager.init_services()
        log_app_event("INFO", "Application Startup", "All services initialized successfully")
        print(" All services initialized successfully")
        yield
    except Exception as e:
        error_msg = f"Failed to initialize services: {e}"
        log_app_event("ERROR", "Startup Failed", error_msg)
        print(f" {error_msg}")
        sys.exit(1)
    finally:
        # Cleanup
        print(" Shutting down application...")
        try:
            ServiceManager.un_init_services()
            log_app_event("INFO", "Application Shutdown", "All services shut down successfully")
            print(" All services shut down successfully")
        except Exception as e:
            error_msg = f"Error during shutdown: {e}"
            log_app_event("ERROR", "Shutdown Error", error_msg)
            print(f" {error_msg}")

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan
)

# CORS configuration using centralized settings
cors_config = settings.server.get_cors_config(settings.is_development)

app.add_middleware(
    CORSMiddleware,
    **cors_config
)

# Security middleware
if settings.security.enable_csrf_protection:
    app.add_middleware(CSRFMiddleware)

if settings.security.enable_rate_limiting:
    app.add_middleware(RateLimitMiddleware)

# General security middleware (always enabled)
app.add_middleware(SecurityMiddleware)

# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Handle WebSocket requests that don't have method attribute
    method = getattr(request, 'method', 'WebSocket')
    log_app_event(
        "ERROR", 
        f"HTTP {exc.status_code} Error",
        f"{method} {request.url}: {exc.detail}"
    )
    
    response = JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )
    
    # Add CORS headers to error responses
    origin = request.headers.get("origin")
    allowed_origins = cors_config.get("allow_origins", [])
    
    if origin and (origin in allowed_origins or "*" in allowed_origins):
        response.headers["Access-Control-Allow-Origin"] = origin if "*" not in allowed_origins else "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = ", ".join(cors_config.get("allow_methods", []))
        response.headers["Access-Control-Allow-Headers"] = ", ".join(cors_config.get("allow_headers", []))
    
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log_app_event(
        "WARNING",
        "Request Validation Error", 
        f"{request.method} {request.url}",
        str(exc.errors())
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "Request validation failed",
            "details": exc.errors(),
            "status_code": 422,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    log_app_event(
        "ERROR",
        "Unhandled Exception",
        f"{request.method} {request.url}: {str(exc)}",
        str(exc.__class__.__name__)
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "path": str(request.url)
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify application status"""
    try:
        return {
            "status": "healthy",
            "message": "Industrial Vision System is running",
            "version": "1.0.0",
            "services": {
                "audio": "operational",
                "api": "operational"
            }
        }
    except Exception as e:
        log_app_event("ERROR", "Health Check Failed", str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": "System experiencing issues",
                "error": str(e)
            }
        )

app.include_router(camera_routes.router)
app.include_router(camera_settings_routes.router)
app.include_router(image_source_routes.router)
app.include_router(image_generator_routes.router)
app.include_router(components_routes.router)
app.include_router(references_routes.router)
app.include_router(identifications_routes.router)
app.include_router(custom_components_routes.router)
app.include_router(algorithm_routes.router)
app.include_router(cnc_routes.router)
app.include_router(locations_routes.router)
app.include_router(robot_routes.router)
app.include_router(itac_routes.router)
app.include_router(profilometer_routes.router)
app.include_router(inspection_list_routes.router)
app.include_router(process_routes.router)
app.include_router(configuration_routes.router)
app.include_router(media_routes.router)
app.include_router(authentication_routes.router)
app.include_router(log_routes.router)
app.include_router(mask_routes.router)
app.include_router(help_routes.router)
app.include_router(peripheral_routes.router)
app.include_router(camera_calibration_routes.router)
app.include_router(stereo_callibration_routes.router)
app.include_router(annotation_routes.router)

if __name__ == "__main__":
    # Get server configuration from centralized settings
    server_config = settings.server.get_uvicorn_config()
    host = server_config["host"]
    port = server_config["port"]
    
    try:
        # Kill any existing processes on the port
        print(f" Checking for existing processes on port {port}...")
        kill_existing_processes(port)
        
        # Start the server using centralized configuration
        print(f" Starting AOI Backend Server at http://{host}:{port}")
        print(" API documentation available at:")
        print(f"   • Swagger UI: http://localhost:{port}/docs")
        print(f"   • ReDoc: http://localhost:{port}/redoc")
        print(" Press Ctrl+C to stop the server")
        
        uvicorn.run(
            app, 
            **server_config
        )
        
    except KeyboardInterrupt:
        print("\n Application stopped by user")
    except Exception as e:
        print(f" Failed to start server: {e}")
        print(f"💡 Make sure port {port} is not in use by another application")
        sys.exit(1)
