import sys
import subprocess
import os
from pathlib import Path

def check_virtualenv():
    """Check if running inside a virtual environment with Windows support"""
    venv_path = os.getenv('VIRTUAL_ENV', '')
    if not venv_path:
        print("Virtual environment not activated!")
        print("Run '.venv\\Scripts\\activate' (Windows) or 'source .venv/bin/activate' (Unix)")
        sys.exit(1)
    
    # Verify actual Python executable location
    expected_python = str(Path(venv_path) / 'Scripts' / 'python.exe')
    if not Path(expected_python).exists():
        print(f"Missing Python in virtual environment: {expected_python}")
        sys.exit(1)

def check_windows_paths():
    """Verify no spaces in critical paths for Windows deployments"""
    critical_paths = [
        Path(__file__).parent.parent,
        Path(os.getenv('VIRTUAL_ENV', ''))
    ]
    for path in critical_paths:
        if ' ' in str(path):
            print(f"Space detected in critical path: {path}")
            print("Windows deployments require space-free paths")
            sys.exit(1)

def check_dependencies():
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("Failed to install dependencies. Check your internet connection and try again.")
        sys.exit(1)

if __name__ == "__main__":
    check_virtualenv()
    check_dependencies()
    print("Environment is ready!")
