#!/usr/bin/env python3
"""
AOI Platform Setup Script
Automated setup for industrial inspection and automation platform
Supports Windows and Linux with prerequisite checking and warnings
"""

import os
import sys
import subprocess
import platform
import shutil
import threading
import time
from pathlib import Path

class AutoSetup:
    """Automatic setup utilities for Windows and Linux"""
    
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"
        self.arch = platform.machine().lower()
        self._stop_progress = False
        
        if not (self.is_windows or self.is_linux):
            print("ERROR: This setup script only supports Windows and Linux")
            sys.exit(1)
            
        # Detect architecture
        if self.arch in ['amd64', 'x86_64']:
            self.arch = 'x64'
        elif self.arch in ['arm64', 'aarch64']:
            self.arch = 'arm64'
        else:
            self.arch = 'x64'  # Default fallback

    def run_command(self, command, shell=None, cwd=None):
        """Run a command and return success status"""
        try:
            if shell is None:
                shell = self.is_windows
            
            result = subprocess.run(command, shell=shell, cwd=cwd, 
                                  capture_output=True, text=True, check=True)
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip() if e.stderr else str(e)
        except Exception as e:
            return False, str(e)

    def show_progress(self, message, delay=0.5):
        """Show a spinning progress indicator"""
        def animate():
            chars = "|/-\\"
            idx = 0
            while not self._stop_progress:
                print(f"\r{message} {chars[idx % len(chars)]}", end="", flush=True)
                idx += 1
                time.sleep(delay)
            # Clear the progress line when stopping
            print(f"\r{' ' * (len(message) + 2)}\r", end="", flush=True)
        
        self._stop_progress = False
        thread = threading.Thread(target=animate)
        thread.daemon = True
        thread.start()
        return thread

    def stop_progress(self):
        """Stop the progress indicator and ensure clean output"""
        self._stop_progress = True
        time.sleep(0.15)  # Give more time for the thread to finish and clear

    def run_command_with_progress(self, command, message, shell=None, cwd=None, show_output=False, timeout=600):
        """Run a command with progress indicator and optional real-time output"""
        progress_thread = None
        if not show_output:
            progress_thread = self.show_progress(message)
        else:
            print(f"{message}...")
        
        try:
            if shell is None:
                shell = self.is_windows
            
            if show_output:
                # Show real-time output with timeout
                result = subprocess.run(command, shell=shell, cwd=cwd, text=True, timeout=timeout)
                success = result.returncode == 0
                output = ""
            else:
                # Capture output with timeout
                result = subprocess.run(command, shell=shell, cwd=cwd, 
                                      capture_output=True, text=True, timeout=timeout)
                success = result.returncode == 0
                output = result.stdout.strip() if success else result.stderr.strip()
            
            if progress_thread:
                self.stop_progress()
                
            # Ensure clean output after stopping progress
            if success:
                # Use simpler characters that work reliably on Windows
                print(f"OK: {message} - completed successfully")
            else:
                print(f"ERROR: {message} - failed")
                if output and not show_output:
                    print(f"Error: {output}")
                    
            return success, output
            
        except subprocess.TimeoutExpired:
            if progress_thread:
                self.stop_progress()
            print(f"ERROR: {message} - timed out after {timeout} seconds")
            print("This operation is taking longer than expected. You can:")
            print("1. Try running the setup again")
            print("2. Check your internet connection")
            print("3. Manually install dependencies")
            return False, "Timeout"
        except Exception as e:
            if progress_thread:
                self.stop_progress()
            print(f"ERROR: {message} - error: {e}")
            return False, str(e)

    def check_port_availability(self, port=8000):
        """Check if a port is available and find processes using it"""
        print(f"Checking if port {port} is available...")
        
        if self.is_windows:
            # Windows: Use netstat to find processes using the port
            cmd = ["netstat", "-ano"]
            success, output = self.run_command(cmd, shell=False)
            
            if success:
                processes_info = []
                for line in output.split('\n'):
                    if f":{port}" in line and "LISTENING" in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            # Get process name using tasklist
                            task_cmd = ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"]
                            task_success, task_output = self.run_command(task_cmd, shell=False)
                            
                            if task_success and task_output:
                                # Parse CSV output to get process name
                                task_parts = task_output.split(',')
                                if len(task_parts) >= 1:
                                    process_name = task_parts[0].strip('"')
                                    processes_info.append({
                                        'pid': pid,
                                        'name': process_name,
                                        'line': line.strip()
                                    })
                return processes_info
        else:
            # Linux: Use lsof or netstat to find processes using the port
            # Try lsof first (more reliable)
            cmd = ["lsof", "-i", f":{port}"]
            success, output = self.run_command(cmd, shell=False)
            
            if success:
                processes_info = []
                lines = output.split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            process_name = parts[0]
                            pid = parts[1]
                            processes_info.append({
                                'pid': pid,
                                'name': process_name,
                                'line': line.strip()
                            })
                return processes_info
            else:
                # Fallback to netstat if lsof is not available
                cmd = ["netstat", "-tlnp"]
                success, output = self.run_command(cmd, shell=False)
                
                if success:
                    processes_info = []
                    for line in output.split('\n'):
                        if f":{port}" in line and "LISTEN" in line:
                            parts = line.split()
                            if len(parts) >= 7:
                                pid_info = parts[-1]
                                if '/' in pid_info:
                                    pid, process_name = pid_info.split('/', 1)
                                    processes_info.append({
                                        'pid': pid,
                                        'name': process_name,
                                        'line': line.strip()
                                    })
                    return processes_info
        
        return []

    def kill_process(self, pid):
        """Kill a process by PID"""
        try:
            if self.is_windows:
                cmd = ["taskkill", "/F", "/PID", str(pid)]
            else:
                cmd = ["kill", "-9", str(pid)]
            
            success, output = self.run_command(cmd, shell=False)
            return success, output
        except Exception as e:
            return False, str(e)

    def handle_port_conflict(self, port=8000):
        """Handle port conflicts by asking user to kill conflicting processes"""
        processes = self.check_port_availability(port)
        
        if not processes:
            print(f"Port {port} is available")
            return True
        
        print(f"WARNING: Port {port} is already in use!")
        print("Processes using this port:")
        
        for i, proc in enumerate(processes, 1):
            print(f"  {i}. Process: {proc['name']} (PID: {proc['pid']})")
            print(f"     Details: {proc['line']}")
        
        print(f"\nTo run the backend server on port {port}, these processes need to be terminated.")
        
        while True:
            try:
                response = input("\nDo you want to kill these processes? (y/n): ").lower().strip()
                
                if response in ['y', 'yes']:
                    print("Terminating processes...")
                    all_killed = True
                    
                    for proc in processes:
                        print(f"Killing process {proc['name']} (PID: {proc['pid']})...")
                        success, output = self.kill_process(proc['pid'])
                        
                        if success:
                            print(f"Successfully terminated {proc['name']}")
                        else:
                            print(f"Failed to terminate {proc['name']}: {output}")
                            all_killed = False
                    
                    if all_killed:
                        print(f"Port {port} should now be available")
                        return True
                    else:
                        print("Some processes could not be terminated. Backend may fail to start.")
                        return False
                        
                elif response in ['n', 'no']:
                    print("Processes were not terminated.")
                    print(f"Backend server will likely fail to start on port {port}")
                    print("You can manually stop these processes or use a different port.")
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no")
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled")
                return False
            except EOFError:
                print("\nNo input received, assuming 'no'")
                return False


    def check_python_version(self):
        """Check if Python version is compatible"""
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version_str = result.stdout.strip()
                print(f"Found: {version_str}")
                
                # Extract version numbers
                import re
                version_match = re.search(r'Python (\d+)\.(\d+)\.(\d+)', version_str)
                if version_match:
                    major, minor, patch = map(int, version_match.groups())
                    
                    # Check if version is 3.8-3.13
                    if major == 3 and 8 <= minor <= 13:
                        print("OK: Python version is compatible")
                        return True
                    else:
                        print("WARNING: Python version not supported")
                        print("Required: Python 3.8-3.13")
                        return False
                        
        except Exception:
            pass
            
        print("ERROR: Python not found")
        print("Please install Python 3.8-3.13:")
        if self.is_windows:
            print("  Windows: Download from https://www.python.org/downloads/")
            print("  During installation, make sure to check 'Add Python to PATH'")
        else:
            print("  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv")
            print("  CentOS/RHEL: sudo yum install python3 python3-pip")
            print("  Fedora: sudo dnf install python3 python3-pip")
            print("  Arch: sudo pacman -S python python-pip")
        return False

    def check_nodejs_version(self):
        """Check if Node.js version is compatible"""
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version_str = result.stdout.strip()
                print(f"Found: Node.js {version_str}")
                
                # Extract version number
                import re
                version_match = re.search(r'v(\d+)\.(\d+)\.(\d+)', version_str)
                if version_match:
                    major, minor, patch = map(int, version_match.groups())
                    
                    # Check if version is 16 or higher
                    if major >= 16:
                        print("OK: Node.js version is compatible")
                        return True
                    else:
                        print("WARNING: Node.js version is too old")
                        print("Required: Node.js 16 or higher")
                        print("Recommended: Node.js 20 (LTS)")
                        return False
                        
        except Exception:
            pass
            
        print("ERROR: Node.js not found")
        print("Please install Node.js 16 or higher:")
        if self.is_windows:
            print("  Windows: Download from https://nodejs.org/")
            print("  Choose the LTS version for best stability")
        else:
            print("  Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs")
            print("  Fedora: sudo dnf install nodejs npm")
            print("  CentOS/RHEL: sudo yum install nodejs npm")
            print("  Arch: sudo pacman -S nodejs npm")
        return False

    def check_git_version(self):
        """Check if Git is available (optional)"""
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version_str = result.stdout.strip()
                print(f"Found: {version_str}")
                print("OK: Git is available")
                return True
        except Exception:
            pass
            
        print("WARNING: Git not found (optional)")
        print("Git is recommended for version control:")
        if self.is_windows:
            print("  Windows: Download from https://git-scm.com/")
        else:
            print("  Ubuntu/Debian: sudo apt install git")
            print("  CentOS/RHEL: sudo yum install git")
            print("  Fedora: sudo dnf install git")
            print("  Arch: sudo pacman -S git")
        return False

    def check_prerequisites(self):
        """Check all prerequisites and warn about issues"""
        print("Checking prerequisites...")
        print("=" * 50)
        
        # Check Python
        print("Checking Python...")
        python_ok = self.check_python_version()
        
        # Check Node.js
        print("\nChecking Node.js...")
        nodejs_ok = self.check_nodejs_version()
        
        # Check npm (should come with Node.js)
        print("\nChecking npm...")
        npm_ok = False
        # Try different npm commands for Windows and Linux
        npm_commands = ["npm.cmd", "npm"] if self.is_windows else ["npm"]
        
        for cmd in npm_commands:
            try:
                result = subprocess.run([cmd, "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    print(f"Found: npm {version}")
                    print("OK: npm is available")
                    npm_ok = True
                    break
            except:
                continue
            
        if not npm_ok:
            print("WARNING: npm not found")
            print("npm should be installed automatically with Node.js")
            print("If Node.js is installed but npm is missing, try reinstalling Node.js")
        
        # Check Git (optional)
        print("\nChecking Git...")
        git_ok = self.check_git_version()
        
        print("\n" + "=" * 50)
        print("Prerequisites Summary:")
        print(f"  Python: {'OK' if python_ok else 'MISSING/INCOMPATIBLE'}")
        print(f"  Node.js: {'OK' if nodejs_ok else 'MISSING/INCOMPATIBLE'}")
        print(f"  npm: {'OK' if npm_ok else 'MISSING'}")
        print(f"  Git: {'OK' if git_ok else 'MISSING (optional)'}")
        
        # Only continue if essential prerequisites are met
        if not python_ok or not nodejs_ok:
            print("\nERROR: Essential prerequisites are missing or incompatible!")
            print("Please install the missing software and run this script again.")
            return False
            
        if not npm_ok:
            print("\nWARNING: npm is missing but may be needed for frontend setup")
            print("Consider reinstalling Node.js to get npm")
        
        print("\nAll essential prerequisites are available!")
        return True

    def setup_backend(self):
        """Setup backend environment and dependencies"""
        import subprocess
        import sys
        
        print("\n" + "=" * 60)
        print("BACKEND SETUP")
        print("=" * 60)
        
        # Check if port 8000 is available before setting up
        print("Checking backend port availability...")
        if not self.handle_port_conflict(8000):
            print("WARNING: Port 8000 conflict not resolved")
            print("Backend setup will continue, but the server may fail to start")
        
        backend_dir = Path("backend-flask")
        if not backend_dir.exists():
            print("ERROR: Backend directory not found")
            return False
        
        # Create virtual environment in root directory
        venv_dir = Path("venv")  # Create venv in project root
        if not venv_dir.exists():
            success, output = self.run_command_with_progress(
                [sys.executable, "-m", "venv", "venv"],
                "Creating virtual environment",
                cwd="."
            )
            if not success:
                print(f"ERROR: Failed to create virtual environment: {output}")
                return False
        
        # Get virtual environment paths
        if self.is_windows:
            venv_python = venv_dir / "Scripts" / "python.exe"
            venv_pip = venv_dir / "Scripts" / "pip.exe"
        else:
            venv_python = venv_dir / "bin" / "python"
            venv_pip = venv_dir / "bin" / "pip"
        
        # Upgrade pip in virtual environment
        success, output = self.run_command_with_progress(
            [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
            "Upgrading pip in virtual environment",
            cwd="."  # Run from project root where venv exists
        )
        if not success:
            print("WARNING: Could not upgrade pip - continuing with current version")
        
        # Install requirements
        # Try backend-specific requirements first, then fall back to root requirements
        backend_requirements = backend_dir / "requirements.txt"
        if backend_requirements.exists():
            requirements_path = backend_requirements
            print(f"Using backend requirements: {requirements_path}")
        else:
            requirements_path = Path("requirements.txt").resolve()
            print(f"Using root requirements: {requirements_path}")
        
        success, output = self.run_command_with_progress(
            [str(venv_python), "-m", "pip", "install", "-r", str(requirements_path)],
            "Installing Python dependencies (this may take a few minutes)",
            cwd=".",
            show_output=True  # Show real-time pip output
        )
        if not success:
            print(f"ERROR: Failed to install requirements")
            return False
        
        # Copy environment file
        env_example = Path(".env.example")
        env_file = backend_dir / ".env"
        if env_example.exists() and not env_file.exists():
            print("Creating environment configuration...")
            shutil.copy(env_example, env_file)
        
        # Create logs directory
        logs_dir = backend_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        print("Backend setup complete!")
        return True

    def setup_frontend(self):
        """Setup frontend environment and dependencies"""
        import subprocess
        
        print("\n" + "=" * 60)
        print("FRONTEND SETUP")
        print("=" * 60)
        
        frontend_dir = Path("aoi-web-front")
        if not frontend_dir.exists():
            print("ERROR: Frontend directory not found")
            return False
        
        # Install npm dependencies
        # Try different npm command approaches
        npm_commands = []
        if self.is_windows:
            npm_commands = [
                ["npm.cmd", "install"],
                ["npm", "install"],
                ["cmd", "/c", "npm", "install"]
            ]
        else:
            npm_commands = [
                ["npm", "install"]
            ]
        
        success = False
        for cmd in npm_commands:
            try:
                success, output = self.run_command_with_progress(
                    cmd,
                    "Installing Node.js dependencies (this may take a few minutes)",
                    cwd=frontend_dir,
                    shell=False,
                    show_output=True  # Show real-time npm output
                )
                if success:
                    break
                # Continue trying other commands if this one fails
            except FileNotFoundError:
                continue
            except Exception as e:
                continue
        
        if not success:
            # Fallback: try with shell=True
            try:
                success, output = self.run_command_with_progress(
                    "npm install",
                    "Installing Node.js dependencies (fallback method)",
                    cwd=frontend_dir,
                    shell=True,
                    show_output=True
                )
            except Exception:
                pass
        
        if not success:
            print("WARNING: Could not install npm dependencies automatically")
            print("Please run manually: cd aoi-web-front && npm install")
            print("This is required before running the frontend server")
            return False
        
        # Update npm packages to their latest compatible versions
        print("\nUpdating npm packages to latest compatible versions...")
        update_commands = []
        if self.is_windows:
            update_commands = [
                ["npm.cmd", "update"],
                ["npm", "update"],
                ["cmd", "/c", "npm", "update"]
            ]
        else:
            update_commands = [
                ["npm", "update"]
            ]
        
        for cmd in update_commands:
            try:
                success, output = self.run_command_with_progress(
                    cmd,
                    "Updating npm packages",
                    cwd=frontend_dir,
                    shell=False,
                    show_output=False
                )
                if success:
                    break
            except:
                continue
        
        # Fix any security vulnerabilities
        print("\nChecking and fixing security vulnerabilities...")
        audit_commands = []
        if self.is_windows:
            audit_commands = [
                ["npm.cmd", "audit", "fix"],
                ["npm", "audit", "fix"],
                ["cmd", "/c", "npm", "audit", "fix"]
            ]
        else:
            audit_commands = [
                ["npm", "audit", "fix"]
            ]
        
        for cmd in audit_commands:
            try:
                success, output = self.run_command_with_progress(
                    cmd,
                    "Fixing npm security vulnerabilities",
                    cwd=frontend_dir,
                    shell=False,
                    show_output=False
                )
                if success:
                    print("OK: Security vulnerabilities fixed (if any existed)")
                    break
            except:
                continue
        
        # Run audit to show final status
        print("\nChecking final security status...")
        audit_check_commands = []
        if self.is_windows:
            audit_check_commands = [
                ["npm.cmd", "audit"],
                ["npm", "audit"],
                ["cmd", "/c", "npm", "audit"]
            ]
        else:
            audit_check_commands = [
                ["npm", "audit"]
            ]
        
        for cmd in audit_check_commands:
            try:
                success, output = self.run_command(cmd, shell=False, cwd=frontend_dir)
                if "found 0 vulnerabilities" in output:
                    print("OK: No security vulnerabilities found")
                elif "vulnerability" in output.lower():
                    print(f"INFO: Security status: {output}")
                break
            except:
                continue
        
        print("Frontend setup complete!")
        return True

    def create_start_scripts(self):
        """Create convenient start scripts for both Windows and Linux"""
        print("\nCreating cross-platform start scripts...")
        
        # Always create both Windows and Linux scripts for cross-platform compatibility
        self.create_windows_scripts()
        self.create_linux_scripts()
        
        print("Cross-platform start scripts created successfully")
        return True
    
    def create_windows_scripts(self):
        """Create Windows batch scripts"""
        
        # Use the improved Windows scripts
        backend_script = """@echo off
echo ========================================
echo     AOI Backend Server
echo ========================================
echo.

REM Go to project root
cd /d "%~dp0"

REM Check if venv exists in root
if not exist "venv" (
    echo Virtual environment not found! Running setup...
    echo.
    call python setup.py
    if errorlevel 1 (
        echo Setup failed! Please check the errors above.
        pause
        exit /b 1
    )
    echo.
    echo Setup completed successfully!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\\Scripts\\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment!
    echo Please check if Python and venv are properly installed.
    pause
    exit /b 1
)
echo Virtual environment activated successfully
echo.

REM Change to backend directory
cd backend-flask
echo Starting backend server on http://localhost:8000...
echo.

REM Start the backend server
python main.py
if errorlevel 1 (
    echo.
    echo Backend failed to start!
    echo Please check the errors above.
    pause
    exit /b 1
)
echo.
echo Backend server stopped.
pause
"""

        frontend_script = """@echo off
echo ========================================
echo     AOI Frontend Server
echo ========================================
echo.

REM Change to frontend directory
cd /d "%~dp0aoi-web-front"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Node modules not found! Installing dependencies...
    echo.
    call npm install
    if errorlevel 1 (
        echo Failed to install node modules!
        echo Please ensure Node.js and npm are properly installed.
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
)

REM Start the development server
echo Starting frontend development server on http://localhost:5173...
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev
if errorlevel 1 (
    echo.
    echo Frontend failed to start!
    echo Please check the errors above.
    pause
    exit /b 1
)
echo.
echo Frontend server stopped.
pause
"""

        system_script = """@echo off
title AOI Platform Launcher
echo ================================================
echo            AOI Platform Launcher
echo         Industrial Vision ^& Automation
echo ================================================
echo.

REM Check if this is first-time setup
if not exist "venv" (
    echo [SETUP] First time setup detected...
    echo [SETUP] Running initial configuration...
    echo.
    call python setup.py
    if errorlevel 1 (
        echo [ERROR] Setup failed! Please check the errors above.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [SETUP] Configuration completed successfully!
    echo.
)

if not exist "aoi-web-front\\node_modules" (
    echo [SETUP] Installing frontend dependencies...
    echo.
    cd aoi-web-front
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies!
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo [SETUP] Frontend dependencies installed!
    echo.
)

echo [1/2] Starting Backend Server...
echo       API will be available at: http://localhost:8000
start "AOI Backend" cmd /k "%~dp0start_backend.bat"

echo [WAIT] Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo [2/2] Starting Frontend Server...
echo       UI will be available at: http://localhost:5173
start "AOI Frontend" cmd /k "%~dp0start_frontend.bat"

echo.
echo ================================================
echo            Platform Status
echo ================================================
echo Backend API:   http://localhost:8000
echo Frontend UI:   http://localhost:5173
echo.
echo Both servers are starting in separate windows.
echo Please wait ~30 seconds for full initialization.
echo.
echo ================================================
echo To stop the platform:
echo   1. Close both server windows
echo   2. Or press Ctrl+C in each window
echo ================================================
echo.
echo Press any key to close this launcher...
pause > nul
"""

        # Write Windows scripts
        Path("start_backend.bat").write_text(backend_script, encoding='utf-8')
        Path("start_frontend.bat").write_text(frontend_script, encoding='utf-8')
        Path("start_aoi_system.bat").write_text(system_script, encoding='utf-8')
        
        print("Created Windows batch files:")
        print("   - start_backend.bat")
        print("   - start_frontend.bat")
        print("   - start_aoi_system.bat")
    
    def create_linux_scripts(self):
        """Create Linux shell scripts"""
        
        backend_script = """#!/bin/bash
echo "========================================"
echo "     AOI Backend Server"
echo "========================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if venv exists in root
if [ ! -d "venv" ]; then
    echo "Virtual environment not found! Running setup..."
    echo
    python3.13 setup.py 2>/dev/null || python3.12 setup.py 2>/dev/null || python3.11 setup.py 2>/dev/null || python3.10 setup.py 2>/dev/null || python3.9 setup.py 2>/dev/null || python3.8 setup.py 2>/dev/null || python3 setup.py || python setup.py
    if [ $? -ne 0 ]; then
        echo "Setup failed! Please check the errors above."
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo
    echo "Setup completed successfully!"
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment!"
    echo "Please check if Python and venv are properly installed."
    read -p "Press Enter to exit..."
    exit 1
fi
echo "Virtual environment activated successfully"
echo

# Change to backend directory
cd backend-flask
echo "Starting backend server on http://localhost:8000..."
echo

# Start the backend server
python main.py
if [ $? -ne 0 ]; then
    echo
    echo "Backend failed to start!"
    echo "Please check the errors above."
    read -p "Press Enter to exit..."
    exit 1
fi

echo
echo "Backend server stopped."
read -p "Press Enter to exit..."
"""

        frontend_script = """#!/bin/bash
echo "========================================"
echo "     AOI Frontend Server"
echo "========================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Change to frontend directory
cd aoi-web-front

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Node modules not found! Installing dependencies..."
    echo
    npm install
    if [ $? -ne 0 ]; then
        echo "Failed to install node modules!"
        echo "Please ensure Node.js and npm are properly installed."
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo
    echo "Dependencies installed successfully!"
    echo
fi

# Start the development server
echo "Starting frontend development server on http://localhost:5173..."
echo
echo "Press Ctrl+C to stop the server"
echo

npm run dev
if [ $? -ne 0 ]; then
    echo
    echo "Frontend failed to start!"
    echo "Please check the errors above."
    read -p "Press Enter to exit..."
    exit 1
fi

echo
echo "Frontend server stopped."
read -p "Press Enter to exit..."
"""

        system_script = """#!/bin/bash
echo "================================================"
echo "            AOI Platform Launcher"
echo "         Industrial Vision & Automation"
echo "================================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if this is first-time setup
if [ ! -d "venv" ]; then
    echo "[SETUP] First time setup detected..."
    echo "[SETUP] Running initial configuration..."
    echo
    python3.13 setup.py 2>/dev/null || python3.12 setup.py 2>/dev/null || python3.11 setup.py 2>/dev/null || python3.10 setup.py 2>/dev/null || python3.9 setup.py 2>/dev/null || python3.8 setup.py 2>/dev/null || python3 setup.py || python setup.py
    if [ $? -ne 0 ]; then
        echo "[ERROR] Setup failed! Please check the errors above."
        echo
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo
    echo "[SETUP] Configuration completed successfully!"
    echo
fi

if [ ! -d "aoi-web-front/node_modules" ]; then
    echo "[SETUP] Installing frontend dependencies..."
    echo
    cd aoi-web-front
    npm install
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install frontend dependencies!"
        cd ..
        read -p "Press Enter to exit..."
        exit 1
    fi
    cd ..
    echo "[SETUP] Frontend dependencies installed!"
    echo
fi

echo "[1/2] Starting Backend Server..."
echo "       API will be available at: http://localhost:8000"

# Start backend in background
./start_backend.sh &
BACKEND_PID=$!

echo "[WAIT] Waiting for backend to initialize..."
sleep 5

echo "[2/2] Starting Frontend Server..."
echo "       UI will be available at: http://localhost:5173"

# Start frontend in background
./start_frontend.sh &
FRONTEND_PID=$!

echo
echo "================================================"
echo "            Platform Status"
echo "================================================"
echo "Backend API:   http://localhost:8000"
echo "Frontend UI:   http://localhost:5173"
echo
echo "Both servers are running in the background."
echo "Please wait ~30 seconds for full initialization."
echo
echo "================================================"
echo "To stop the platform:"
echo "   Press Ctrl+C to stop both servers"
echo "================================================"
echo

# Function to handle cleanup
cleanup() {
    echo
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Servers stopped."
    exit 0
}

# Set trap to handle Ctrl+C
trap cleanup SIGINT

# Wait for user input or processes to end
echo "Press Ctrl+C to stop the platform..."
wait
"""

        # Write Linux scripts and make executable
        backend_file = Path("start_backend.sh")
        frontend_file = Path("start_frontend.sh")
        system_file = Path("start_aoi_system.sh")
        
        backend_file.write_text(backend_script, encoding='utf-8')
        frontend_file.write_text(frontend_script, encoding='utf-8')
        system_file.write_text(system_script, encoding='utf-8')
        
        # Make executable
        try:
            backend_file.chmod(0o755)
            frontend_file.chmod(0o755)
            system_file.chmod(0o755)
        except Exception:
            # chmod might not work on Windows, but that's okay
            pass
        
        print("Created Linux shell scripts:")
        print("   - start_backend.sh")
        print("   - start_frontend.sh")
        print("   - start_aoi_system.sh")

def main():
    """Main setup function"""
    print("AOI Platform Setup")
    print("=" * 50)
    setup = AutoSetup()
    print(f"Platform: {setup.system}")
    
    # Check if we're in the right directory
    if not Path("backend-flask").exists() or not Path("aoi-web-front").exists():
        print("ERROR: Please run this script from the project root directory")
        print("Expected to find: backend-flask/ and aoi-web-front/ directories")
        sys.exit(1)
    
    # Check all prerequisites and warn about issues
    if not setup.check_prerequisites():
        print("\nERROR: Prerequisites check failed")
        sys.exit(1)
    
    # Setup backend
    if not setup.setup_backend():
        print("\nERROR: Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup.setup_frontend():
        print("\nERROR: Frontend setup failed")
        sys.exit(1)
    
    # Create start scripts
    setup.create_start_scripts()
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Review and update .env file in backend-flask directory")
    print("2. Connect your industrial hardware (cameras, robots, CNC, etc.)")
    
    print("3. For Windows: Run start_aoi_system.bat (or individual .bat files)")
    print("4. For Linux: Run ./start_aoi_system.sh (or individual .sh files)")
    
    print("5. Open http://localhost:5173 in your browser")
    print("\nSetup completed successfully! Happy automating!")

if __name__ == "__main__":
    main()