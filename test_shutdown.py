#!/usr/bin/env python3
"""
Test script to verify backend shutdown doesn't leave orphaned threads
"""
import time
import threading
import subprocess
import signal
import sys
import os

def list_threads():
    """List all active threads"""
    threads = [t for t in threading.enumerate()]
    print(f"Active threads: {len(threads)}")
    for i, thread in enumerate(threads):
        print(f"  {i+1}. {thread.name}: {'daemon' if thread.daemon else 'non-daemon'}, alive: {thread.is_alive()}")

def test_backend_shutdown():
    """Test that backend shuts down cleanly without orphaned threads"""
    
    print("=== Testing Backend Shutdown ===")
    
    # Start the backend process
    print("Starting backend...")
    backend_process = subprocess.Popen([
        "venv/Scripts/python.exe", 
        "-c", 
        "import sys; sys.path.append('backend-flask'); from main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8001)"
    ], 
    cwd="C:/Users/andre/Desktop/site",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
    )
    
    # Wait for backend to start
    time.sleep(3)
    
    print(f"Backend process started with PID: {backend_process.pid}")
    
    # Send SIGTERM to gracefully shut down
    print("Sending SIGTERM signal...")
    backend_process.terminate()
    
    # Wait for process to finish
    try:
        stdout, stderr = backend_process.communicate(timeout=10)
        print(f"Backend process finished with return code: {backend_process.returncode}")
        
        # Check if there were any thread-related issues in stderr
        print("=== STDERR Output (last 500 chars) ===")
        print(stderr[-500:] if stderr else "No stderr output")
        print("=== End STDERR ===")
        
        if "Problem during reading the serial port" in stderr:
            print("ERROR: Found orphaned serial port threads in stderr")
            return False
        else:
            print("SUCCESS: No orphaned thread messages found")
            return True
            
    except subprocess.TimeoutExpired:
        print("ERROR: Backend process didn't shut down within timeout")
        backend_process.kill()
        return False

if __name__ == "__main__":
    success = test_backend_shutdown()
    sys.exit(0 if success else 1)