import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.models import Stipend, Organization, Tag

logger = logging.getLogger(__name__)

def verify_db_connection():
    """Verify database connection is working"""
    try:
        # Test connection with a simple query
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("Database connection verified successfully")
                return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def verify_model_relationships():
    """Verify all model relationships are properly configured"""
    try:
        # Test Stipend relationships
        stipend = Stipend(
            name="Test Stipend",
            organization_id=1,
            application_deadline="2025-12-31 23:59:59"
        )
        
        # Test Organization relationship
        org = Organization(name="Test Org")
        stipend.organization = org
        
        # Test Tag relationship
        tag = Tag(name="Test Tag")
        stipend.tags.append(tag)
        
        logger.info("Model relationships verified successfully")
        return True
    except Exception as e:
        logger.error(f"Model relationship verification failed: {str(e)}")
        return False

def verify_backup_config():
    """Verify database backup configuration"""
    try:
        # Check if backup directory exists
        from app.config import BACKUP_DIR
        import os
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
            
        # Test backup creation
        from app.utils.backup import create_backup
        backup_file = create_backup()
        
        if os.path.exists(backup_file):
            logger.info(f"Backup created successfully at {backup_file}")
            return True
        return False
    except Exception as e:
        logger.error(f"Backup verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if not verify_db_connection():
        print("Database connection verification failed")
        exit(1)
        
    if not verify_model_relationships():
        print("Model relationship verification failed")
        exit(1)
        
    if not verify_backup_config():
        print("Backup configuration verification failed")
        exit(1)
        
    print("All database verifications passed successfully")
