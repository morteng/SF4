import logging
from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

logger = logging.getLogger(__name__)

def validate_schema():
    """Validate database schema against expected structure"""
    try:
        # Get expected tables from models
        expected_tables = {
            'user': ['id', 'username', 'email', 'password_hash'],
            'stipend': ['id', 'name', 'description', 'tags'],
            'organization': ['id', 'name', 'description'],
            'tag': ['id', 'name']
        }
        
        # Get actual schema
        from app import db
        inspector = inspect(db.engine)
        actual_tables = inspector.get_table_names()
        
        # Verify all expected tables exist
        missing_tables = set(expected_tables.keys()) - set(actual_tables)
        if missing_tables:
            logger.error(f"Missing tables: {', '.join(missing_tables)}")
            return False
            
        # Verify table columns
        for table, columns in expected_tables.items():
            actual_columns = [col['name'] for col in inspector.get_columns(table)]
            missing_columns = set(columns) - set(actual_columns)
            if missing_columns:
                logger.error(f"Missing columns in {table}: {', '.join(missing_columns)}")
                return False
                
        logger.info("Schema validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Schema validation failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if validate_schema():
        exit(0)
    else:
        exit(1)
import logging
from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

logger = logging.getLogger(__name__)

def validate_schema():
    """Validate database schema against expected structure"""
    try:
        # Get expected tables from models
        expected_tables = {
            'user': ['id', 'username', 'email', 'password_hash'],
            'stipend': ['id', 'name', 'description', 'tags'],
            'organization': ['id', 'name', 'description'],
            'tag': ['id', 'name']
        }
        
        # Get actual schema
        from app import db
        inspector = inspect(db.engine)
        actual_tables = inspector.get_table_names()
        
        # Verify all expected tables exist
        missing_tables = set(expected_tables.keys()) - set(actual_tables)
        if missing_tables:
            logger.error(f"Missing tables: {', '.join(missing_tables)}")
            return False
            
        # Verify table columns
        for table, columns in expected_tables.items():
            actual_columns = [col['name'] for col in inspector.get_columns(table)]
            missing_columns = set(columns) - set(actual_columns)
            if missing_columns:
                logger.error(f"Missing columns in {table}: {', '.join(missing_columns)}")
                return False
                
        logger.info("Schema validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Schema validation failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if validate_schema():
        exit(0)
    else:
        exit(1)