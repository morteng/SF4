import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factory import create_app
from init_test_db import init_test_db

import pytest

def run_tests():
    """Run version management tests with enhanced logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='logs/tests/version_management.log'
    )
    
    try:
        # Initialize test database
        app = create_app('testing')
        with app.app_context():
            init_test_db()
            
            # Run tests with coverage
            result = pytest.main([
                'tests/version_management/',
                '-v',
                '--cov=scripts.version',
                '--cov-report=term-missing',
                '--cov-branch'
            ])
        
        if result == 0:
            logging.info("All version management tests passed")
            print("All version management tests passed")
            return True
        else:
            logging.error("Some version management tests failed")
            print("Some version management tests failed")
            return False
    except Exception as e:
        logging.error(f"Error running version management tests: {str(e)}")
        print(f"Error running version management tests: {str(e)}")
        return False

if __name__ == "__main__":
    run_tests()
