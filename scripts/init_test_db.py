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
    """Initialize test database with comprehensive validation"""
    try:
        app = create_app('testing')
        
        with app.app_context():
            # Initialize extensions
            if 'sqlalchemy' not in app.extensions:
                db.init_app(app)
                
            # Clean existing data
            try:
                db.drop_all()
            except Exception as e:
                logging.warning(f"Could not drop all tables: {str(e)}")
                db.session.rollback()
            
            # Create schema
            db.create_all()
            
            # Create test data
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
            
            # Set relationships
            stipend.tags.extend([tag1, tag2])
            stipend.organization = org
            
            # Commit data
            db.session.add_all([org, tag1, tag2, stipend])
            db.session.commit()
            
            # Verify data integrity
            assert Organization.query.count() == 1
            assert Tag.query.count() == 2
            assert Stipend.query.count() == 1
            
            logging.info("Test database initialized successfully")
            return True
            
    except Exception as e:
        logging.error(f"Test database initialization failed: {str(e)}")
        db.session.rollback()
        return False
    finally:
        if 'sqlalchemy' in app.extensions:
            db.session.remove()

if __name__ == "__main__":
    init_test_db()
