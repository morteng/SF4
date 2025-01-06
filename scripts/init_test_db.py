import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factory import create_app
from app.extensions import db
from app.models import Stipend, Tag, Organization  # Import all models

def init_test_db():
    """Initialize a fresh test database with proper relationships"""
    try:
        app = create_app('testing')
        with app.app_context():
            # Ensure database directory exists
            os.makedirs('instance', exist_ok=True)
            
            # Drop and create all tables
            db.drop_all()
            db.create_all()
            
            # Create test data with proper relationships
            org = Organization(name="Test Org")
            tag = Tag(name="Test Tag")
            stipend = Stipend(name="Test Stipend")
            
            # Establish relationships
            stipend.tags.append(tag)
            stipend.organization = org
            
            db.session.add_all([org, tag, stipend])
            db.session.commit()
            
            print("Test database initialized successfully with relationships")
            return True
    except Exception as e:
        print(f"Test database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    init_test_db()
