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
from pathlib import Path

class AutoSetup:
    """Automatic setup utilities for Windows and Linux"""
    
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"
        self.arch = platform.machine().lower()
        
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
                    
                    # Check if version is 3.8 or higher
                    if major >= 3 and minor >= 8:
                        print("OK: Python version is compatible")
                        return True
                    else:
                        print("WARNING: Python version is too old")
                        print("Required: Python 3.8 or higher")
                        print("Recommended: Python 3.11")
                        return False
                        
        except Exception:
            pass
            
        print("ERROR: Python not found")
        print("Please install Python 3.8 or higher:")
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
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"Found: npm {version}")
                print("OK: npm is available")
                npm_ok = True
        except:
            pass
            
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
        
        print("\nSetting up backend...")
        
        # Check if port 8000 is available before setting up
        print("Checking backend port availability...")
        if not self.handle_port_conflict(8000):
            print("WARNING: Port 8000 conflict not resolved")
            print("Backend setup will continue, but the server may fail to start")
        
        backend_dir = Path("backend-flask")
        if not backend_dir.exists():
            print("ERROR: Backend directory not found")
            return False
        
        # Create virtual environment
        venv_dir = backend_dir / "venv"
        if not venv_dir.exists():
            print("Creating virtual environment...")
            try:
                result = subprocess.run([sys.executable, "-m", "venv", "venv"], 
                                      cwd=backend_dir, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"ERROR: Failed to create virtual environment: {result.stderr}")
                    return False
            except Exception as e:
                print(f"ERROR: Virtual environment creation failed: {e}")
                return False
        
        # Get virtual environment paths
        if self.is_windows:
            venv_python = venv_dir / "Scripts" / "python.exe"
            venv_pip = venv_dir / "Scripts" / "pip.exe"
        else:
            venv_python = venv_dir / "bin" / "python"
            venv_pip = venv_dir / "bin" / "pip"
        
        # Upgrade pip in virtual environment
        print("Upgrading pip...")
        try:
            result = subprocess.run([str(venv_pip), "install", "--upgrade", "pip"], 
                                  cwd=backend_dir, capture_output=True, text=True)
            if result.returncode != 0:
                print("WARNING: Could not upgrade pip")
        except Exception:
            print("WARNING: Could not upgrade pip")
        
        # Install requirements
        print("Installing Python dependencies...")
        requirements_path = Path("requirements.txt").resolve()
        try:
            result = subprocess.run([str(venv_pip), "install", "-r", str(requirements_path)], 
                                  cwd=backend_dir, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"ERROR: Failed to install requirements: {result.stderr}")
                return False
        except Exception as e:
            print(f"ERROR: Failed to install requirements: {e}")
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
        
        print("Backend setup complete")
        return True

    def setup_frontend(self):
        """Setup frontend environment and dependencies"""
        import subprocess
        
        print("\nSetting up frontend...")
        
        frontend_dir = Path("aoi-web-front")
        if not frontend_dir.exists():
            print("ERROR: Frontend directory not found")
            return False
        
        # Install npm dependencies
        print("Installing Node.js dependencies...")
        
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
                result = subprocess.run(cmd, cwd=frontend_dir, 
                                      capture_output=True, text=True, shell=False)
                if result.returncode == 0:
                    success = True
                    break
                # Continue trying other commands if this one fails
            except FileNotFoundError:
                continue
            except Exception as e:
                continue
        
        if not success:
            # Fallback: try with shell=True (will fail in Git Bash but try anyway)
            try:
                result = subprocess.run("npm install", shell=True, cwd=frontend_dir, 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    success = True
            except Exception:
                pass
        
        if not success:
            print("WARNING: Could not install npm dependencies automatically")
            print("Please run manually: cd aoi-web-front && npm install")
            print("This is required before running the frontend server")
        
        print("Frontend setup complete")
        return True

    def create_start_scripts(self):
        """Create convenient start scripts"""
        print("\nCreating start scripts...")
        
        if self.is_windows:
            # Windows batch files
            backend_script = """@echo off
echo Starting AOI Backend Server...
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

            frontend_script = """@echo off
echo Starting AOI Frontend Server...
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

            system_script = """@echo off
echo Starting Complete AOI Platform...
echo.
echo Starting Backend...
start "AOI Backend" cmd /k "%~dp0start_backend.bat"
timeout /t 3 /nobreak > nul
echo Starting Frontend...
start "AOI Frontend" cmd /k "%~dp0start_frontend.bat"
echo.
echo Both servers are starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:5173
echo.
pause
"""

            # Write scripts
            Path("start_backend.bat").write_text(backend_script, encoding='utf-8')
            Path("start_frontend.bat").write_text(frontend_script, encoding='utf-8')
            Path("start_aoi_system.bat").write_text(system_script, encoding='utf-8')
            
            print("Created Windows batch files:")
            print("   - start_backend.bat")
            print("   - start_frontend.bat")
            print("   - start_aoi_system.bat")
            
        else:
            # Linux shell scripts
            backend_script = """#!/bin/bash
echo "Starting CNC Backend Server..."
cd "$(dirname "$0")/backend-flask"
if [ ! -d "venv" ]; then
    echo "Virtual environment not found! Please run setup.py first."
    read -p "Press enter to continue..."
    exit 1
fi
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment!"
    read -p "Press enter to continue..."
    exit 1
fi
echo "Virtual environment activated"
python main.py
if [ $? -ne 0 ]; then
    echo "Backend failed to start!"
    read -p "Press enter to continue..."
    exit 1
fi
"""

            frontend_script = """#!/bin/bash
echo "Starting CNC Frontend Server..."
cd "$(dirname "$0")/aoi-web-front"
if [ ! -d "node_modules" ]; then
    echo "Node modules not found! Please run setup.py first."
    read -p "Press enter to continue..."
    exit 1
fi
echo "Starting development server..."
npm run dev
if [ $? -ne 0 ]; then
    echo "Frontend failed to start!"
    read -p "Press enter to continue..."
    exit 1
fi
"""

            system_script = """#!/bin/bash
echo "Starting Complete CNC System..."
echo
echo "Starting Backend..."
gnome-terminal -- bash -c "$(dirname "$0")/start_backend.sh; exec bash" 2>/dev/null || \\
xterm -e "$(dirname "$0")/start_backend.sh; exec bash" 2>/dev/null || \\
"$(dirname "$0")/start_backend.sh" &
sleep 3
echo "Starting Frontend..."
gnome-terminal -- bash -c "$(dirname "$0")/start_frontend.sh; exec bash" 2>/dev/null || \\
xterm -e "$(dirname "$0")/start_frontend.sh; exec bash" 2>/dev/null || \\
"$(dirname "$0")/start_frontend.sh" &
echo
echo "Both servers are starting..."
echo "Backend will be available at: http://localhost:8000"
echo "Frontend will be available at: http://localhost:5173"
echo
read -p "Press enter to continue..."
"""

            # Write scripts and make executable
            backend_file = Path("start_backend.sh")
            frontend_file = Path("start_frontend.sh")
            system_file = Path("start_aoi_system.sh")
            
            backend_file.write_text(backend_script, encoding='utf-8')
            frontend_file.write_text(frontend_script, encoding='utf-8')
            system_file.write_text(system_script, encoding='utf-8')
            
            # Make executable
            backend_file.chmod(0o755)
            frontend_file.chmod(0o755)
            system_file.chmod(0o755)
            
            print("Created Linux shell scripts:")
            print("   - start_backend.sh")
            print("   - start_frontend.sh")
            print("   - start_aoi_system.sh")
        
        print("Start scripts created successfully")
        return True

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
    
    if setup.is_windows:
        print("3. Run start_backend.bat to start the backend")
        print("4. Run start_frontend.bat to start the frontend")
        print("   Or run start_aoi_system.bat to start both")
    else:
        print("3. Run ./start_backend.sh to start the backend")
        print("4. Run ./start_frontend.sh to start the frontend")
        print("   Or run ./start_aoi_system.sh to start both")
    
    print("5. Open http://localhost:5173 in your browser")
    print("\nSetup completed successfully! Happy automating!")

if __name__ == "__main__":
    main()