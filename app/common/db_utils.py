import os
import time
import logging
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

def validate_db_connection(db_uri):
    """Validate database connection with enhanced error handling"""
    try:
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            if not Path(db_path).exists():
                logger.error(f"SQLite database file not found: {db_path}")
                return False
                
        # Verify connection using existing logic
        return _verify_db_connection(db_uri)
    except Exception as e:
        logger.error(f"Database validation failed: {str(e)}")
        return False

def _verify_db_connection(db_uri):
    """Enhanced database verification with retry logic and schema validation"""
    logger = logging.getLogger(__name__)
    
    # Configurable retries and timeout from environment
    max_retries = int(os.getenv('DB_RETRIES', '5'))
    base_delay = int(os.getenv('DB_RETRY_DELAY', '2'))
    timeout = int(os.getenv('DB_TIMEOUT', '30'))
    
    # Verify connection pool settings
    pool_size = int(os.getenv('DB_POOL_SIZE', '10'))
    max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    
    # Verify connection pool settings
    pool_size = int(os.getenv('DB_POOL_SIZE', '5'))
    max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '10'))
    
    for attempt in range(max_retries):
        try:
            if not db_uri:
                logger.error("SQLALCHEMY_DATABASE_URI not set")
                return False
                
            # Verify SQLite file exists with proper path handling
            if db_uri.startswith('sqlite'):
                db_path = db_uri.replace('sqlite:///', '')
                # Handle Windows paths
                if os.name == 'nt':
                    db_path = db_path.lstrip('/')
                    db_path = db_path.replace('/', '\\')
                if not Path(db_path).exists():
                    # Create database file if it doesn't exist
                    try:
                        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
                        Path(db_path).touch()
                        logger.info(f"Created database file: {db_path}")
                    except Exception as e:
                        logger.error(f"Failed to create database file: {str(e)}")
                        return False
                        
            engine = create_engine(db_uri)
            with engine.connect() as conn:
                # Verify schema version for SQLite
                if db_uri.startswith('sqlite'):
                    cursor = conn.connection.cursor()
                    cursor.execute("PRAGMA schema_version")
                    version = cursor.fetchone()[0]
                    if version < 1:
                        logger.error("Invalid schema version")
                        return False
                    cursor.close()
                        
                # Verify core tables exist
                required_tables = ['stipend', 'tag', 'organization', 'user']
                result = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
                existing_tables = [row[0] for row in result]
                
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
