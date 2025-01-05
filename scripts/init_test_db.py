import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db

def init_test_db():
    """Initialize a fresh test database"""
    try:
        app = create_app('testing')
        with app.app_context():
            # Ensure database directory exists
            os.makedirs('instance', exist_ok=True)
            db.drop_all()
            db.create_all()
            print("Test database initialized successfully")
            return True
    except Exception as e:
        print(f"Test database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    init_test_db()
