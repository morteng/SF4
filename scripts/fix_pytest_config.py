import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.factory import create_app
from app.extensions import db

def fix_pytest_config():
    """Fix pytest configuration"""
    try:
        # Create test app
        app = create_app('testing')
        
        # Update test database URI
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        # Initialize extensions
        db.init_app(app)
        
        # Create test client
        test_client = app.test_client()
        
        return True
    except Exception as e:
        print(f"Pytest configuration fix failed: {str(e)}")
        return False

if __name__ == "__main__":
    fix_pytest_config()
