import os
import time
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

def validate_db_connection(db_uri):
    """Validate database connection with proper path handling"""
    logger = configure_logger()
    
    try:
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            if not Path(db_path).exists():
                logger.error(f"SQLite database file not found: {db_path}")
                return False
                
        # Verify connection using existing logic
        return verify_db_connection()
    except Exception as e:
        logger.error(f"Database validation failed: {str(e)}")
        return False

def verify_db_connection():
    """Enhanced database verification with retry logic and schema validation"""
    logger = configure_logger()
    
    max_retries = 3
    base_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
            if not db_uri:
                logger.error("SQLALCHEMY_DATABASE_URI not set")
                return False
                
            # Verify SQLite file exists
            if db_uri.startswith('sqlite'):
                db_path = db_uri.replace('sqlite:///', '')
                if not Path(db_path).exists():
                    logger.error(f"Database file not found: {db_path}")
                    return False
                    
            engine = create_engine(db_uri)
            with engine.connect() as conn:
                # Verify schema version
                if db_uri.startswith('sqlite'):
                    result = conn.execute("PRAGMA schema_version")
                    version = result.scalar()
                    if version < 1:
                        logger.error("Invalid schema version")
                        return False
                        
                # Verify core tables exist
                required_tables = ['stipend', 'tag', 'organization', 'user']
                result = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = [row[0] for row in result.fetchall()]
                
                missing_tables = [table for table in required_tables if table not in existing_tables]
                if missing_tables:
                    logger.error(f"Missing required tables: {', '.join(missing_tables)}")
                    return False
                    
                logger.info("Database connection and schema validation successful")
                return True
            
        except SQLAlchemyError as e:
            if attempt == max_retries - 1:
                logger.error(f"Database connection failed after {max_retries} attempts: {str(e)}")
                return False
            delay = base_delay * (2 ** attempt)  # Exponential backoff
            time.sleep(delay)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Unexpected error verifying database connection: {str(e)}")
                return False
            delay = base_delay * (2 ** attempt)  # Exponential backoff
            time.sleep(delay)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_db_connection():
        print("Database connection verification passed")
        exit(0)
    else:
        print("Database connection verification failed")
        exit(1)
