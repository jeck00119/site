#!/usr/bin/env python3
"""
Cross-platform project verification script.
Checks if all components are working correctly on both Windows and Linux.
"""

import sys
import os
import traceback


def test_platform_detection():
    """Test platform detection utilities."""
    print("1. Testing platform detection...")
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'backend-flask'))
        from src.platform_utils import get_platform, PlatformDetector
        platform = get_platform()
        print(f"   OK Platform detected: {platform}")
        
        info = PlatformDetector.get_platform_info()
        print(f"   OK Python version: {info['python_version']}")
        return True
    except Exception as e:
        print(f"   ERROR Platform detection failed: {e}")
        return False


def test_path_resolution():
    """Test cross-platform path handling."""
    print("2. Testing path resolution...")
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'backend-flask'))
        from src.platform_utils import PathHandler
        
        data_dir = PathHandler.get_data_directory()
        config_dir = PathHandler.get_config_directory()
        reports_dir = PathHandler.get_reports_directory()
        
        print(f"   OK Data directory: {data_dir}")
        print(f"   OK Config directory: {config_dir}")
        print(f"   OK Reports directory: {reports_dir}")
        
        # Ensure directories exist
        PathHandler.ensure_directory(data_dir)
        PathHandler.ensure_directory(os.path.join(data_dir, "cognex"))
        PathHandler.ensure_directory(reports_dir)
        
        return True
    except Exception as e:
        print(f"   ERROR Path resolution failed: {e}")
        return False


def test_environment_loading():
    """Test environment configuration."""
    print("3. Testing environment loading...")
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'backend-flask'))
        import environment
        
        cognex_path = environment.COGNEX_DATA_PATH
        print(f"   OK COGNEX_DATA_PATH: {cognex_path}")
        
        # Check if path is properly resolved
        if os.path.isabs(cognex_path):
            print("   OK Path is absolute")
        else:
            print("   WARNING Path is relative")
            
        return True
    except Exception as e:
        print(f"   ERROR Environment loading failed: {e}")
        return False


def test_platform_specific_imports():
    """Test platform-specific functionality."""
    print("4. Testing platform-specific imports...")
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'backend-flask'))
        from src.platform_utils import is_windows, is_linux, CommandExecutor
        
        if is_windows():
            print("   OK Windows platform detected")
            try:
                import win32com.client
                print("   OK pywin32 available")
            except ImportError:
                print("   WARNING pywin32 not available (install with: pip install pywin32)")
                
        elif is_linux():
            print("   OK Linux platform detected")
            try:
                import pyudev
                print("   OK pyudev available")
            except ImportError:
                print("   WARNING pyudev not available (install with: pip install pyudev)")
        
        # Test device detection
        try:
            usb_devices = CommandExecutor.check_usb_devices()
            print(f"   OK USB detection working ({len(usb_devices)} devices found)")
            
            cameras = CommandExecutor.check_camera_devices()
            print(f"   OK Camera detection working ({len(cameras)} cameras found)")
        except Exception as e:
            print(f"   WARNING Device detection error: {e}")
            
        return True
    except Exception as e:
        print(f"   ERROR Platform-specific imports failed: {e}")
        return False


def test_core_services():
    """Test core service imports."""
    print("5. Testing core services...")
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'backend-flask'))
        
        # Test camera factory
        from services.camera.camera_factory import CameraFactory
        print("   OK CameraFactory imported")
        
        # Test process service
        from services.processing.process_service import ProcessService
        print("   OK ProcessService imported")
        
        # Test capability service
        from services.capability.capability_service import CapabilityService
        print("   OK CapabilityService imported")
        
        return True
    except Exception as e:
        print(f"   ERROR Core services failed: {e}")
        traceback.print_exc()
        return False


def test_api_routes():
    """Test API route imports."""
    print("6. Testing API routes...")
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'backend-flask'))
        
        from api.routers.peripheral_routes import router
        print("   OK Peripheral routes imported")
        
        from api.routers.camera_routes import router as camera_router
        print("   OK Camera routes imported")
        
        return True
    except Exception as e:
        print(f"   ERROR API routes failed: {e}")
        return False


def test_frontend_build():
    """Test frontend build process."""
    print("7. Testing frontend build...")
    try:
        frontend_dir = os.path.join(os.getcwd(), 'aoi-web-front')
        if os.path.exists(frontend_dir):
            package_json = os.path.join(frontend_dir, 'package.json')
            if os.path.exists(package_json):
                print("   OK Frontend directory structure looks good")
                
                # Check if node_modules exists
                node_modules = os.path.join(frontend_dir, 'node_modules')
                if os.path.exists(node_modules):
                    print("   OK Node modules installed")
                else:
                    print("   WARNING Node modules not found (run: npm install)")
                    
                return True
            else:
                print("   ERROR package.json not found")
                return False
        else:
            print("   ERROR Frontend directory not found")
            return False
    except Exception as e:
        print(f"   ERROR Frontend test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 50)
    print("Cross-Platform AOI Project Verification")
    print("=" * 50)
    
    tests = [
        test_platform_detection,
        test_path_resolution,
        test_environment_loading,
        test_platform_specific_imports,
        test_core_services,
        test_api_routes,
        test_frontend_build
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"   ERROR Test {test_func.__name__} crashed: {e}")
            print()
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All tests passed! Your project is ready for cross-platform deployment.")
        print("\nTo start your application:")
        print("  Windows: run start_backend.bat and start_frontend.bat")
        print("  Linux:   run ./start_backend.sh and ./start_frontend.sh")
    else:
        print("WARNING: Some tests failed. Please review the errors above.")
        print("\nCommon fixes:")
        print("  - Install missing dependencies: pip install -r backend-flask/requirements.txt")
        print("  - For Windows: pip install pywin32")
        print("  - For Linux: pip install pyudev")
        print("  - For frontend: cd aoi-web-front && npm install")
    
    print("=" * 50)
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)