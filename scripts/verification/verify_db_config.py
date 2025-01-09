import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def verify_db_config():
    """Verify database configuration"""
    try:
        # Check database URI from .env
        db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
        if not db_uri:
            logger.error("Database URI not configured in .env")
            return False
            
        # Verify database file exists
        db_path = db_uri.replace('sqlite:///', '')
        if not Path(db_path).exists():
            logger.error(f"Database file not found at {db_path}")
            return False
            
        logger.info("Database configuration verified")
        return True
        
    except Exception as e:
        logger.error(f"Database configuration verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_db_config():
        print("Database configuration verified")
        exit(0)
    else:
        print("Database configuration verification failed")
        exit(1)
