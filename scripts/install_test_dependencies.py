import subprocess
import sys
import logging
from pathlib import Path

def configure_logging():
    """Configure basic logging for the script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('deps')

def install_dependencies():
    logger = configure_logging()
    try:
        req_file = Path("requirements-test.txt")
        if not req_file.exists():
            logger.error("requirements-test.txt not found! Creating default...")
            req_file.write_text(
                "pytest>=8.0.0\n"
                "freezegun>=1.2.0\n"
                "factory-boy>=3.3.0\n"
                "python-dotenv>=1.0.0\n"
                "factory-boy>=3.3.0\n"
                "python-dotenv>=1.0.0\n"
            )
            
        logger.info("Installing test dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
        return True
    except Exception as e:
        logger.error(f"Dependency installation failed: {str(e)}")
        return False

if __name__ == "__main__":
    if install_dependencies():
        print("Setup completed successfully")
        sys.exit(0)
    else:
        print("Setup failed")
        sys.exit(1)
