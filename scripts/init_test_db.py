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
    app = create_app('testing')
    
    try:
        # Ensure proper application context
        ctx = app.app_context()
        ctx.push()
        
        try:
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
            
            # Create test data with validation
            test_data = [
                Organization(name="Test Org"),
                Tag(name="Test Tag 1", category="Test Category"),
                Tag(name="Test Tag 2", category="Test Category"),
                Stipend(
                    name="Test Stipend",
                    summary="Test Summary",
                    description="Test Description",
                    homepage_url="http://test.com",
                    application_procedure="Test Procedure",
                    eligibility_criteria="Test Criteria",
                    application_deadline=datetime.utcnow(),
                    open_for_applications=True
                )
            ]
            
            # Validate test data
            for obj in test_data:
                if not obj.validate():
                    raise ValueError(f"Invalid test data: {obj}")
            
            # Set relationships
            test_data[-1].tags.extend(test_data[1:3])
            test_data[-1].organization = test_data[0]
            
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
            try:
                with app.app_context():
                    db.session.remove()
            except RuntimeError:
                pass

if __name__ == "__main__":
    init_test_db()
