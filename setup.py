#!/usr/bin/env python3
"""
CNC Project Setup Script
Automated setup for both backend and frontend components
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(command, cwd=None, shell=False):
    """Run a command and return success status"""
    try:
        if shell or platform.system() == "Windows":
            result = subprocess.run(command, shell=True, cwd=cwd, check=True, 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), cwd=cwd, check=True, 
                                  capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_prerequisites():
    """Check if required software is installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    try:
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python 3.8+ is required")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    except Exception:
        print("❌ Python not found")
        return False
    
    # Check Node.js
    success, output = run_command("node --version", shell=True)
    if not success:
        print("❌ Node.js not found. Please install Node.js 16+")
        return False
    
    node_version = output.strip()
    print(f"✅ Node.js {node_version}")
    
    # Check npm
    success, output = run_command("npm --version", shell=True)
    if not success:
        print("❌ npm not found")
        return False
    
    npm_version = output.strip()
    print(f"✅ npm {npm_version}")
    
    return True

def setup_backend():
    """Setup backend environment and dependencies"""
    print("\\n🐍 Setting up backend...")
    
    backend_dir = Path("backend-flask")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Create virtual environment
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print("📦 Creating virtual environment...")
        success, _ = run_command(f"{sys.executable} -m venv venv", cwd=backend_dir)
        if not success:
            print("❌ Failed to create virtual environment")
            return False
    
    # Determine pip command based on OS
    if platform.system() == "Windows":
        pip_cmd = "venv\\\\Scripts\\\\pip"
        python_cmd = "venv\\\\Scripts\\\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Install requirements
    print("📦 Installing Python dependencies...")
    success, output = run_command(f"{pip_cmd} install -r ../requirements.txt", 
                                 cwd=backend_dir, shell=True)
    if not success:
        print(f"❌ Failed to install requirements: {output}")
        return False
    
    # Copy environment file
    env_example = Path(".env.example")
    env_file = backend_dir / ".env"
    if env_example.exists() and not env_file.exists():
        print("📝 Creating environment configuration...")
        shutil.copy(env_example, env_file)
    
    print("✅ Backend setup complete")
    return True

def setup_frontend():
    """Setup frontend environment and dependencies"""
    print("\\n🌐 Setting up frontend...")
    
    frontend_dir = Path("aoi-web-front")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install npm dependencies
    print("📦 Installing Node.js dependencies...")
    success, output = run_command("npm install", cwd=frontend_dir, shell=True)
    if not success:
        print(f"❌ Failed to install npm dependencies: {output}")
        return False
    
    print("✅ Frontend setup complete")
    return True

def create_start_scripts():
    """Create convenient start scripts"""
    print("\\n📜 Creating start scripts...")
    
    # Backend start script
    if platform.system() == "Windows":
        backend_script = """@echo off
cd backend-flask
call venv\\\\Scripts\\\\activate
python main.py
pause
"""
        with open("start_backend.bat", "w") as f:
            f.write(backend_script)
        
        frontend_script = """@echo off
cd aoi-web-front
npm run dev
pause
"""
        with open("start_frontend.bat", "w") as f:
            f.write(frontend_script)
    else:
        backend_script = """#!/bin/bash
cd backend-flask
source venv/bin/activate
python main.py
"""
        with open("start_backend.sh", "w") as f:
            f.write(backend_script)
        os.chmod("start_backend.sh", 0o755)
        
        frontend_script = """#!/bin/bash
cd aoi-web-front
npm run dev
"""
        with open("start_frontend.sh", "w") as f:
            f.write(frontend_script)
        os.chmod("start_frontend.sh", 0o755)
    
    print("✅ Start scripts created")

def main():
    """Main setup function"""
    print("🏭 CNC Project Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("backend-flask").exists() or not Path("aoi-web-front").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\\n❌ Prerequisites check failed. Please install required software.")
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print("\\n❌ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("\\n❌ Frontend setup failed")
        sys.exit(1)
    
    # Create start scripts
    create_start_scripts()
    
    print("\\n🎉 Setup complete!")
    print("\\n📋 Next steps:")
    print("1. Review and update .env file in backend-flask directory")
    print("2. Connect your CNC hardware")
    if platform.system() == "Windows":
        print("3. Run start_backend.bat to start the backend")
        print("4. Run start_frontend.bat to start the frontend")
    else:
        print("3. Run ./start_backend.sh to start the backend")
        print("4. Run ./start_frontend.sh to start the frontend")
    print("5. Open http://localhost:5173 in your browser")
    print("\\n🎛️ Happy CNC controlling!")

if __name__ == "__main__":
    main()

