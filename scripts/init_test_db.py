import os
import sys
import logging
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factory import create_app
from app.extensions import db
from app.models import Stipend, Tag, Organization

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/tests/db_init.log'
)

def init_test_db():
    """Initialize a fresh test database with proper relationships and validation"""
    try:
        app = create_app('testing')
        with app.app_context():
            # Ensure database directory exists
            os.makedirs('instance', exist_ok=True)
            
            # Drop and create all tables with proper cleanup
            db.session.remove()
            db.drop_all()
            db.create_all()
            
            # Create test data with proper relationships
            org = Organization(name="Test Org")
            tag1 = Tag(name="Test Tag 1", category="Test Category")
            tag2 = Tag(name="Test Tag 2", category="Test Category")
            stipend = Stipend(
                name="Test Stipend",
                summary="Test Summary",
                description="Test Description",
                homepage_url="http://test.com",
                application_procedure="Test Procedure",
                eligibility_criteria="Test Criteria",
                application_deadline=datetime.utcnow(),
                open_for_applications=True
            )
            
            # Establish relationships
            stipend.tags.extend([tag1, tag2])
            stipend.organization = org
            
            # Add and commit with proper session management
            try:
                db.session.add_all([org, tag1, tag2, stipend])
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
            
            # Verify data was inserted
            org_count = Organization.query.count()
            tag_count = Tag.query.count()
            stipend_count = Stipend.query.count()
            
            if org_count == 1 and tag_count == 2 and stipend_count == 1:
                logging.info("Test database initialized successfully with relationships")
                print("Test database initialized successfully with relationships")
                return True
            else:
                logging.error("Test data verification failed")
                print("Test data verification failed")
                return False
                
    except Exception as e:
        logging.error(f"Test database initialization failed: {str(e)}")
        print(f"Test database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    init_test_db()
