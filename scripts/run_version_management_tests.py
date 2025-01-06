import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factory import create_app
from init_test_db import init_test_db
from scripts.version import validate_db_connection
from app.extensions import db

import pytest

def run_tests():
    """Run version management tests with enhanced logging and proper app context"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='logs/tests/version_management.log'
    )
    
    try:
        # Initialize test database with proper app context
        app = create_app('testing')
        with app.app_context():
            # Validate database connection first
            if not validate_db_connection('instance/stipend.db'):
                logging.error("Database connection validation failed")
                return False
                
            # Ensure extensions are initialized
            if 'sqlalchemy' not in app.extensions:
                db.init_app(app)
                
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
