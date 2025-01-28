import logging
import os
import pathlib
import time
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Dict, Any

from sqlalchemy import create_engine

Path = pathlib.Path

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Base class for database errors"""
    def __init__(self, message: str, operation: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.operation = operation
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        logger.error(f"DatabaseError: {message}", extra={
            'operation': operation,
            'details': details,
            'timestamp': self.timestamp
        })

class ConnectionError(DatabaseError):
    """Raised when database connection fails"""
    pass

class QueryError(DatabaseError):
    """Raised when a database query fails"""
    pass

class SchemaError(DatabaseError):
    """Raised when schema validation fails"""
    pass

class BackupError(DatabaseError):
    """Raised when backup operations fail"""
    pass

def validate_db_connection(db_uri: str) -> bool:
    """Validate database connection with enhanced error handling and logging
    
    Args:
        db_uri: Database connection URI
        
    Returns:
        bool: True if connection is valid, False otherwise
        
    Raises:
        ConnectionError: If connection fails after retries
        SchemaError: If schema validation fails
    """
    logger.info(f"Validating database connection: {db_uri}")
    
    try:
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            if not Path(db_path).exists():
                error_msg = f"SQLite database file not found: {db_path}"
                logger.error(error_msg)
                raise ConnectionError(
                    message=error_msg,
                    operation="validate_db_connection",
                    details={'db_uri': db_uri, 'db_path': db_path}
                )
                
        # Verify connection with retry logic
        return _verify_db_connection(db_uri)
    except ConnectionError:
        raise
    except Exception as e:
        error_msg = f"Database validation failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise ConnectionError(
            message=error_msg,
            operation="validate_db_connection",
            details={'db_uri': db_uri, 'error': str(e)}
        )

def _verify_db_connection(db_uri: str) -> bool:
    """Enhanced database verification with retry logic and schema validation
    
    Args:
        db_uri: Database connection URI
        
    Returns:
        bool: True if connection is valid, False otherwise
        
    Raises:
        ConnectionError: If connection fails after retries
        SchemaError: If schema validation fails
    """
    logger.info(f"Verifying database connection: {db_uri}")
    
    # Configurable settings from environment
    max_retries = int(os.getenv('DB_RETRIES', '5'))
    base_delay = int(os.getenv('DB_RETRY_DELAY', '2'))
    timeout = int(os.getenv('DB_TIMEOUT', '30'))
    pool_size = int(os.getenv('DB_POOL_SIZE', '10'))
    max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    
    # Log connection settings
    logger.debug(f"Connection settings - retries: {max_retries}, delay: {base_delay}, "
                f"timeout: {timeout}, pool_size: {pool_size}, max_overflow: {max_overflow}")
    
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
