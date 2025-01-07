import sys
import os
import logging
import pytest
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factory import create_app
from init_test_db import init_test_db
from scripts.version import (
    validate_db_connection,
    bump_version,
    validate_version,
    create_db_backup,
    validate_production_environment
)
from app.extensions import db
from scripts.verify_test_db import verify_test_db

def configure_logging():
    """Configure logging for version management tests"""
    log_dir = Path('logs/tests')
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'version_management.log'
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return log_file

def run_tests():
    """Run version management tests with enhanced logging and proper app context"""
    log_file = configure_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize test database with proper app context
        app = create_app('testing')
        with app.app_context():
            # Validate database connection first
            if not validate_db_connection('instance/stipend.db'):
                logger.error("Database connection validation failed")
                return False
                
            # Ensure extensions are initialized
            if 'sqlalchemy' not in app.extensions:
                db.init_app(app)
                
            # Initialize and verify test database
            init_test_db()
            if not verify_test_db():
                logger.error("Test database verification failed")
                return False
                
            # Run tests with coverage
            result = pytest.main([
                'tests/version_management/',
                '-v',
                '--cov=scripts.version',
                '--cov-report=term-missing',
                '--cov-branch',
                '--durations=10',
                '--junitxml=logs/tests/version_management.xml'
            ])
        
        if result == 0:
            logger.info("All version management tests passed")
            print(f"All version management tests passed. Logs saved to {log_file}")
            return True
        else:
            logger.error("Some version management tests failed")
            print(f"Some version management tests failed. See {log_file} for details")
            return False
    except Exception as e:
        logger.error(f"Error running version management tests: {str(e)}", exc_info=True)
        print(f"Error running version management tests: {str(e)}")
        return False

if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
