import os
import logging
import sys
import time
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configure paths before importing project modules
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.path_config import configure_paths
from scripts.init_logging import configure_logging

logger = logging.getLogger(__name__)

def validate_db_connection(db_uri: str) -> bool:
    """Validate database connection with error handling"""
    try:
        engine = create_engine(db_uri)
        with engine.connect() as conn:
            # Use text() for proper SQL statement handling
            stmt = text("SELECT 1")
            conn.execute(stmt)
            return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def verify_db_connection(db_uri, max_retries=5, retry_delay=2):
    """Enhanced database connection verification with retries"""
    for attempt in range(max_retries):
        try:
            if validate_db_connection(db_uri):
                return True
        except SQLAlchemyError as e:
            if attempt == max_retries - 1:
                logger.error(f"Database connection failed after {max_retries} attempts: {str(e)}")
                return False
            time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
    return False

if __name__ == "__main__":
    configure_logging()
    
    # Ensure paths are configured for production
    if not configure_paths(production=True):
        logger.error("Failed to configure paths.")
        exit(1)

    logger.info("Starting database connection verification")
    db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    
    if verify_db_connection(db_uri):
        print("Database connection verification passed")
        logger.info("Database connection verification passed")
        exit(0)
    else:
        print("Database connection verification failed")
        logger.error("Database connection verification failed")
        exit(1)
