import subprocess
import sys
import logging
from pathlib import Path

def configure_logger():
    """Configure the logger for dependency installation"""
    logger = logging.getLogger('dependencies')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def install_dependencies():
    """Install required test dependencies"""
    logger = configure_logger()
    try:
        # Install requirements
        logger.info("Installing test dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        # Install test-specific requirements
        test_reqs = Path("requirements-test.txt")
        if test_reqs.exists():
            logger.info("Installing test-specific dependencies...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(test_reqs)])
            
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

if __name__ == "__main__":
    if install_dependencies():
        print("Dependencies installed successfully")
        exit(0)
    else:
        print("Dependency installation failed")
        exit(1)
