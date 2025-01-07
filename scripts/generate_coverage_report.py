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

def generate_coverage():
    """Generate test coverage report"""
    logger = configure_logger()
    try:
        # Initialize test database
        app = create_app('testing')
        with app.app_context():
            init_test_db()
            logger.info("Test database initialized")
            
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
