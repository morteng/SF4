import os
import sys
import subprocess
import logging
from pathlib import Path

def configure_logger():
    """Configure the logger for coverage reporting"""
    logger = logging.getLogger('coverage')
    if not logger.handlers:
        handler = logging.FileHandler('logs/coverage.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

from app.factory import create_app
from init_test_db import init_test_db

def generate_coverage(html=False, xml=False):
    """Generate test coverage report with multiple output formats"""
    logger = configure_logger()
    try:
        # Initialize test database with proper context
        from app.factory import create_app
        app = create_app('testing')
        with app.app_context():
            from scripts.startup.init_db import initialize_database
            initialize_database(validate_schema=True)
            logger.info("Test database initialized with schema validation")
            
            # Run coverage
            result = subprocess.run([
                'coverage', 'run', '--source=app,scripts', 
                '--branch', '-m', 'pytest', 'tests/'
            ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error running coverage tests")
            print(result.stderr)
            return False
            
        # Generate report
        subprocess.run(['coverage', 'report', '-m'])
        
        # Generate HTML report
        subprocess.run(['coverage', 'html'])
        
        return True
        
    except Exception as e:
        print(f"Error generating coverage report: {str(e)}")
        return False

if __name__ == "__main__":
    generate_coverage()
