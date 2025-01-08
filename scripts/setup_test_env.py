import os
import sys
import logging
import subprocess
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
    try:
        # Get project root
        project_root = str(Path(__file__).parent.parent)
        
        # Clear existing paths and add project root first
        sys.path = [p for p in sys.path if not p.startswith(project_root)]
        sys.path.insert(0, project_root)
        
        # Add all necessary directories
        required_dirs = ['app', 'scripts', 'tests', 'migrations']
        for dir_name in required_dirs:
            dir_path = str(Path(project_root) / dir_name)
            if dir_path not in sys.path:
                sys.path.insert(0, dir_path)
                
        # Add scripts directory explicitly
        scripts_dir = str(Path(__file__).parent)
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
                
        # Verify paths
        logger = logging.getLogger(__name__)
        logger.info(f"Configured Python paths: {sys.path}")
        
        # Verify imports work
        try:
            # Add app to path explicitly
            app_dir = str(Path(project_root) / 'app')
            if app_dir not in sys.path:
                sys.path.insert(0, app_dir)
                
            from app import db
            from app.models import User
            from scripts.version import validate_version
            return True
        except ImportError as e:
            logger.error(f"Import verification failed: {str(e)}")
            logger.error(f"Current sys.path: {sys.path}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to setup test paths: {str(e)}")
        return False

def configure_test_environment():
    """Set up test environment variables and application context"""
    try:
        # Install required packages
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        # Set environment variables
        os.environ.update({
            'FLASK_ENV': 'testing',
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'ADMIN_USERNAME': 'testadmin',
            'ADMIN_EMAIL': 'test@example.com',
            'ADMIN_PASSWORD': 'TestPassword123!',
            'SECRET_KEY': 'TestSecretKey1234567890!@#$%^&*()',
            'TESTING': 'true'
        })
        
        # Create and push application context
        from app.factory import create_app
        app = create_app('testing')
        app.app_context().push()
        
        return True
    except Exception as e:
        logger.error(f"Failed to configure test environment: {str(e)}")
        return False

if __name__ == "__main__":
    logger = configure_test_logging()
    setup_test_paths()
    configure_test_environment()
    logger.info("Test environment configured successfully")
