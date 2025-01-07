import os
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

def configure_logger():
    """Configure the logger consistently across the module"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_db_connection():
    """Verify database connection using SQLALCHEMY_DATABASE_URI"""
    logger = configure_logger()
    
    try:
        db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
        if not db_uri:
            logger.error("SQLALCHEMY_DATABASE_URI not set in environment variables")
            return False
            
        # Log database type for debugging
        if db_uri.startswith('sqlite'):
            logger.info("Using SQLite database")
        elif db_uri.startswith('postgresql'):
            logger.info("Using PostgreSQL database")
        else:
            logger.warning(f"Using unknown database type: {db_uri.split(':')[0]}")
            
        # Create engine and test connection
        engine = create_engine(db_uri)
        with engine.connect() as connection:
            logger.info("Successfully connected to database")
            return True
            
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error verifying database connection: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_db_connection():
        print("Database connection verification passed")
        exit(0)
    else:
        print("Database connection verification failed")
        exit(1)
