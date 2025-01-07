import os
import sys
import logging
from pathlib import Path

def configure_test_logging():
    """Configure logging for tests"""
    logger = logging.getLogger('tests')
    if not logger.handlers:
        handler = logging.FileHandler('logs/tests.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def setup_test_paths():
    """Configure Python paths for testing and deployment"""
    project_root = str(Path(__file__).parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        
    # Add all necessary directories
    for dir_name in ['app', 'scripts', 'tests', 'migrations']:
        dir_path = str(Path(__file__).parent.parent / dir_name)
        if dir_path not in sys.path:
            sys.path.insert(0, dir_path)
            
    # Verify paths
    logger = logging.getLogger(__name__)
    logger.info(f"Configured Python paths: {sys.path}")

def configure_test_environment():
    """Set up test environment variables"""
    os.environ.update({
        'FLASK_ENV': 'testing',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'ADMIN_USERNAME': 'testadmin',
        'ADMIN_EMAIL': 'test@example.com',
        'ADMIN_PASSWORD': 'TestPassword123!',
        'SECRET_KEY': 'TestSecretKey1234567890!@#$%^&*()'
    })

if __name__ == "__main__":
    logger = configure_test_logging()
    setup_test_paths()
    configure_test_environment()
    logger.info("Test environment configured successfully")
