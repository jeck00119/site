#!/usr/bin/env python3
"""
CNC Project Setup Script
Automated setup for both backend and frontend components
Cross-platform support for Windows, Linux, and macOS
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class CrossPlatformSetup:
    """Cross-platform setup utilities"""
    
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"
        self.is_macos = self.system == "Darwin"
        
    def get_python_executable(self):
        """Get the correct Python executable for the platform"""
        if self.is_windows:
            return sys.executable
        else:
            # Try python3 first, fallback to python
            for cmd in ["python3", "python"]:
                try:
                    result = subprocess.run([cmd, "--version"], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return cmd
                except FileNotFoundError:
                    continue
            return sys.executable
    
    def get_venv_paths(self, venv_dir):
        """Get virtual environment paths for the platform"""
        if self.is_windows:
            return {
                'python': venv_dir / "Scripts" / "python.exe",
                'pip': venv_dir / "Scripts" / "pip.exe",
                'activate': venv_dir / "Scripts" / "activate.bat"
            }
        else:
            return {
                'python': venv_dir / "bin" / "python",
                'pip': venv_dir / "bin" / "pip",
                'activate': venv_dir / "bin" / "activate"
            }
    
    def get_node_commands(self):
        """Get Node.js commands for the platform"""
        if self.is_windows:
            return {
                'node': 'node.exe',
                'npm': 'npm.cmd'
            }
        else:
            return {
                'node': 'node',
                'npm': 'npm'
            }

def run_command(command, cwd=None, shell=None):
    """Run a command and return success status"""
    try:
        # Auto-detect shell usage based on platform and command type
        if shell is None:
            shell = platform.system() == "Windows" or isinstance(command, str)
        
        if shell:
            result = subprocess.run(command, shell=True, cwd=cwd, check=True, 
                                  capture_output=True, text=True)
        else:
            if isinstance(command, str):
                command = command.split()
            result = subprocess.run(command, cwd=cwd, check=True, 
                                  capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except FileNotFoundError as e:
        return False, f"Command not found: {e}"

def check_prerequisites():
    """Check if required software is installed"""
    print("🔍 Checking prerequisites...")
    setup = CrossPlatformSetup()
    
    # Check Python
    try:
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python 3.8+ is required")
            print(f"   Current version: {python_version.major}.{python_version.minor}.{python_version.micro}")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    except Exception:
        print("❌ Python not found")
        return False
    
    # Check Node.js
    node_commands = setup.get_node_commands()
    success, output = run_command(f"{node_commands['node']} --version")
    if not success:
        print("❌ Node.js not found. Please install Node.js 16+")
        if setup.is_windows:
            print("   Download from: https://nodejs.org/")
        elif setup.is_linux:
            print("   Install with: sudo apt install nodejs npm")
        else:
            print("   Install with: brew install node")
        return False
    
    node_version = output.strip()
    print(f"✅ Node.js {node_version}")
    
    # Check npm
    success, output = run_command(f"{node_commands['npm']} --version")
    if not success:
        print("❌ npm not found")
        return False
    
    npm_version = output.strip()
    print(f"✅ npm {npm_version}")
    
    # Check Git
    success, output = run_command("git --version")
    if not success:
        print("⚠️  Git not found (optional but recommended)")
        if setup.is_windows:
            print("   Download from: https://git-scm.com/")
        elif setup.is_linux:
            print("   Install with: sudo apt install git")
        else:
            print("   Install with: brew install git")
    else:
        git_version = output.strip()
        print(f"✅ {git_version}")
    
    return True

def setup_backend():
    """Setup backend environment and dependencies"""
    print("\\n🐍 Setting up backend...")
    setup = CrossPlatformSetup()
    
    backend_dir = Path("backend-flask")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Create virtual environment
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print("📦 Creating virtual environment...")
        python_exe = setup.get_python_executable()
        success, output = run_command(f"{python_exe} -m venv venv", cwd=backend_dir)
        if not success:
            print(f"❌ Failed to create virtual environment: {output}")
            # Try alternative method
            print("🔄 Trying alternative venv creation...")
            success, output = run_command(f"{python_exe} -m virtualenv venv", cwd=backend_dir)
            if not success:
                print("❌ Virtual environment creation failed. Please install virtualenv:")
                if setup.is_windows:
                    print("   pip install virtualenv")
                else:
                    print("   pip3 install virtualenv")
                return False
    
    # Get virtual environment paths
    venv_paths = setup.get_venv_paths(venv_dir)
    
    # Upgrade pip in virtual environment
    print("📦 Upgrading pip...")
    success, _ = run_command(f'"{venv_paths["pip"]}" install --upgrade pip', cwd=backend_dir)
    if not success:
        print("⚠️  Warning: Could not upgrade pip")
    
    # Install requirements
    print("📦 Installing Python dependencies...")
    requirements_path = Path("../requirements.txt").resolve()
    success, output = run_command(f'"{venv_paths["pip"]}" install -r "{requirements_path}"', 
                                 cwd=backend_dir)
    if not success:
        print(f"❌ Failed to install requirements: {output}")
        print("🔄 Trying with --no-cache-dir...")
        success, output = run_command(f'"{venv_paths["pip"]}" install --no-cache-dir -r "{requirements_path}"', 
                                     cwd=backend_dir)
        if not success:
            print(f"❌ Failed to install requirements: {output}")
            return False
    
    # Copy environment file
    env_example = Path(".env.example")
    env_file = backend_dir / ".env"
    if env_example.exists() and not env_file.exists():
        print("📝 Creating environment configuration...")
        shutil.copy(env_example, env_file)
    
    # Create logs directory
    logs_dir = backend_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    print("✅ Backend setup complete")
    return True

def setup_frontend():
    """Setup frontend environment and dependencies"""
    print("\\n🌐 Setting up frontend...")
    setup = CrossPlatformSetup()
    
    frontend_dir = Path("aoi-web-front")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Get Node.js commands
    node_commands = setup.get_node_commands()
    
    # Clear npm cache (helps with cross-platform issues)
    print("🧹 Clearing npm cache...")
    run_command(f"{node_commands['npm']} cache clean --force", cwd=frontend_dir)
    
    # Install npm dependencies
    print("📦 Installing Node.js dependencies...")
    success, output = run_command(f"{node_commands['npm']} install", cwd=frontend_dir)
    if not success:
        print(f"❌ Failed to install npm dependencies: {output}")
        print("🔄 Trying with --legacy-peer-deps...")
        success, output = run_command(f"{node_commands['npm']} install --legacy-peer-deps", cwd=frontend_dir)
        if not success:
            print(f"❌ Failed to install npm dependencies: {output}")
            return False
    
    print("✅ Frontend setup complete")
    return True

def create_start_scripts():
    """Create convenient start scripts"""
    print("\\n📜 Creating start scripts...")
    setup = CrossPlatformSetup()
    
    if setup.is_windows:
        # Windows batch files
        backend_script = """@echo off
echo Starting CNC Backend Server...
cd /d "%~dp0backend-flask"
if not exist "venv" (
    echo Virtual environment not found! Please run setup.py first.
    pause
    exit /b 1
)
call venv\\Scripts\\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment!
    pause
    exit /b 1
)
echo Virtual environment activated
python main.py
if errorlevel 1 (
    echo Backend failed to start!
    pause
    exit /b 1
)
pause
"""
        with open("start_backend.bat", "w", encoding='utf-8') as f:
            f.write(backend_script)
        
        frontend_script = """@echo off
echo Starting CNC Frontend Server...
cd /d "%~dp0aoi-web-front"
if not exist "node_modules" (
    echo Node modules not found! Please run setup.py first.
    pause
    exit /b 1
)
echo Starting development server...
npm run dev
if errorlevel 1 (
    echo Frontend failed to start!
    pause
    exit /b 1
)
pause
"""
        with open("start_frontend.bat", "w", encoding='utf-8') as f:
            f.write(frontend_script)
            
        # Windows PowerShell scripts (alternative)
        backend_ps_script = """# CNC Backend Starter (PowerShell)
Write-Host "Starting CNC Backend Server..." -ForegroundColor Green
Set-Location "$PSScriptRoot\\backend-flask"
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found! Please run setup.py first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
& ".\\venv\\Scripts\\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to activate virtual environment!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Virtual environment activated" -ForegroundColor Yellow
python main.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend failed to start!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
"""
        with open("start_backend.ps1", "w", encoding='utf-8') as f:
            f.write(backend_ps_script)
    
    else:
        # Unix shell scripts (Linux/macOS)
        backend_script = """#!/bin/bash
echo "Starting CNC Backend Server..."
cd "$(dirname "$0")/backend-flask"
if [ ! -d "venv" ]; then
    echo "Virtual environment not found! Please run setup.py first."
    read -p "Press Enter to exit..."
    exit 1
fi
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment!"
    read -p "Press Enter to exit..."
    exit 1
fi
echo "Virtual environment activated"
python main.py
if [ $? -ne 0 ]; then
    echo "Backend failed to start!"
    read -p "Press Enter to exit..."
    exit 1
fi
"""
        with open("start_backend.sh", "w", encoding='utf-8') as f:
            f.write(backend_script)
        os.chmod("start_backend.sh", 0o755)
        
        frontend_script = """#!/bin/bash
echo "Starting CNC Frontend Server..."
cd "$(dirname "$0")/aoi-web-front"
if [ ! -d "node_modules" ]; then
    echo "Node modules not found! Please run setup.py first."
    read -p "Press Enter to exit..."
    exit 1
fi
echo "Starting development server..."
npm run dev
if [ $? -ne 0 ]; then
    echo "Frontend failed to start!"
    read -p "Press Enter to exit..."
    exit 1
fi
"""
        with open("start_frontend.sh", "w", encoding='utf-8') as f:
            f.write(frontend_script)
        os.chmod("start_frontend.sh", 0o755)
    
    # Create a combined start script
    if setup.is_windows:
        combined_script = """@echo off
echo Starting CNC Control System...
echo.
echo This will start both backend and frontend servers.
echo Make sure you have two terminal windows available.
echo.
pause
echo.
echo Starting backend in this window...
echo Frontend will open in a new window.
echo.
start "CNC Frontend" cmd /k "start_frontend.bat"
timeout /t 3 /nobreak >nul
call start_backend.bat
"""
        with open("start_cnc_system.bat", "w", encoding='utf-8') as f:
            f.write(combined_script)
    else:
        combined_script = """#!/bin/bash
echo "Starting CNC Control System..."
echo
echo "This will start both backend and frontend servers."
echo "Make sure you have terminal multiplexer or multiple terminals available."
echo
read -p "Press Enter to continue..."
echo
echo "Starting backend and frontend..."
echo "Frontend will open in a new terminal if possible."
echo

# Try to open frontend in new terminal
if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal -- bash -c "./start_frontend.sh; exec bash"
elif command -v xterm >/dev/null 2>&1; then
    xterm -e "./start_frontend.sh" &
elif command -v osascript >/dev/null 2>&1; then
    osascript -e 'tell app "Terminal" to do script "./start_frontend.sh"'
else
    echo "Could not open new terminal. Please run ./start_frontend.sh in another terminal."
fi

sleep 3
echo "Starting backend in this terminal..."
./start_backend.sh
"""
        with open("start_cnc_system.sh", "w", encoding='utf-8') as f:
            f.write(combined_script)
        os.chmod("start_cnc_system.sh", 0o755)
    
    print("✅ Start scripts created")
    if setup.is_windows:
        print("   - start_backend.bat (Command Prompt)")
        print("   - start_backend.ps1 (PowerShell)")
        print("   - start_frontend.bat")
        print("   - start_cnc_system.bat (starts both)")
    else:
        print("   - start_backend.sh")
        print("   - start_frontend.sh") 
        print("   - start_cnc_system.sh (starts both)")

def main():
    """Main setup function"""
    print("🏭 CNC Project Setup")
    print("=" * 50)
    setup = CrossPlatformSetup()
    print(f"🖥️  Platform: {setup.system}")
    
    # Check if we're in the right directory
    if not Path("backend-flask").exists() or not Path("aoi-web-front").exists():
        print("❌ Please run this script from the project root directory")
        print("   Expected structure:")
        print("   - backend-flask/")
        print("   - aoi-web-front/")
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
    
    if setup.is_windows:
        print("3. Run start_backend.bat to start the backend")
        print("4. Run start_frontend.bat to start the frontend")
        print("   Or run start_cnc_system.bat to start both")
    else:
        print("3. Run ./start_backend.sh to start the backend")
        print("4. Run ./start_frontend.sh to start the frontend")
        print("   Or run ./start_cnc_system.sh to start both")
    
    print("5. Open http://localhost:5173 in your browser")
    print("\\n🎛️ Happy CNC controlling!")

if __name__ == "__main__":
    main()

