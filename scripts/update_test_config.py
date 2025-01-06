import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factory import create_app
from app.extensions import db

def update_test_config():
    """Update test configuration"""
    try:
        # Create test app
        app = create_app('testing')
        
        # Update test database URI
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize extensions if not already initialized
        if 'sqlalchemy' not in app.extensions:
            db.init_app(app)
        
        # Create test client
        with app.app_context():
            db.create_all()
            test_client = app.test_client()
        
        return True
    except Exception as e:
        print(f"Test configuration update failed: {str(e)}")
        return False

if __name__ == "__main__":
    update_test_config()
