import logging
import os
from scripts.security.verify_admin import verify_admin_user
from scripts.version import validate_db_connection
from scripts.verify_deployment import verify_deployment

def run_startup_checks():
    """Run all required startup checks"""
    # Configure logger if not already configured
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    try:
        # Verify database connection
        db_uri = os.getenv('SQLALCHEMY_DATABASE_URI').replace('sqlite:///', '')
        if not validate_db_connection(db_uri):
            logger.error("Database connection validation failed")
            return False
            
        # Verify admin user
        if not verify_admin_user():
            logger.error("Admin user verification failed")
            return False
            
        # Verify deployment configuration
        if not verify_deployment():
            logger.error("Deployment verification failed")
            return False
            
        logger.info("All startup checks passed")
        return True
        
    except Exception as e:
        logger.error(f"Startup check failed: {str(e)}")
        return False

if __name__ == "__main__":
    if run_startup_checks():
        print("Startup checks passed")
        exit(0)
    else:
        print("Startup checks failed")
        exit(1)
