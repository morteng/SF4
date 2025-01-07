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
        
        # Update test configuration
        app.config.update({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key',
            'DEBUG': False
        })
        
        # Initialize extensions if not already initialized
        if 'sqlalchemy' not in app.extensions:
            db.init_app(app)
            
        # Verify configuration
        if not app.config['TESTING']:
            raise RuntimeError("Test configuration not properly set")
        
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
