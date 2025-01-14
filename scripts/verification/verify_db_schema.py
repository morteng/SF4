import os
import logging
import sys
from pathlib import Path
from sqlalchemy import inspect, create_engine
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logger = logging.getLogger(__name__)

def configure_paths():
    """Configure project paths with proper error handling."""
    try:
        project_root = str(Path(__file__).resolve().parent.parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        app_dir = str(Path(project_root) / 'app')
        if app_dir not in sys.path:
            sys.path.insert(0, app_dir)
            
        return True
    except Exception as e:
        logger.error(f"Failed to configure paths: {str(e)}")
        return False

def verify_foreign_keys(inspector):
    """Verify foreign key relationships in the database."""
    try:
        for table in inspector.get_table_names():
            foreign_keys = inspector.get_foreign_keys(table)
            for fk in foreign_keys:
                if not fk.get('constrained_columns'):
                    logger.error(f"Invalid foreign key in {table}")
                    return False
        return True
    except SQLAlchemyError as e:
        logger.error(f"Foreign key verification failed: {str(e)}")
        return False

def validate_schema(validate_relations=False, validate_required_fields=True):
    """Validate database schema against expected structure."""
    if not configure_paths():
        logger.error("Path configuration failed")
        return False

    try:
        db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
        if not db_uri:
            logger.error("SQLALCHEMY_DATABASE_URI not set")
            return False
            
        engine = create_engine(db_uri)
        inspector = inspect(engine)
        
        # Define expected schema
        expected_schema = {
            'user': ['id', 'username', 'email', 'password_hash'],
            'stipend': ['id', 'name', 'description', 'tags'],
            'organization': ['id', 'name', 'description'],
            'tag': ['id', 'name']
        }

        actual_tables = inspector.get_table_names()

        # Verify all expected tables exist
        missing_tables = set(expected_schema.keys()) - set(actual_tables)
        if missing_tables:
            logger.error(f"Missing tables: {', '.join(missing_tables)}")
            return False

        # Verify table columns
        for table, expected_columns in expected_schema.items():
            actual_columns = [col['name'] for col in inspector.get_columns(table)]
            missing_columns = set(expected_columns) - set(actual_columns)
            if missing_columns:
                logger.error(f"Missing columns in {table}: {', '.join(missing_columns)}")
                return False

        # Verify required fields
        if validate_required_fields:
            stipend_columns = inspector.get_columns('stipend')
            name_col = next((col for col in stipend_columns if col['name'] == 'name'), None)
            if not name_col or name_col.get('nullable', True):
                logger.error("Stipend name must be a required field")
                return False

        # Verify foreign key relationships
        if validate_relations and not verify_foreign_keys(inspector):
            logger.error("Foreign key validation failed")
            return False

        logger.info("Schema validation passed")
        return True

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = validate_schema(validate_relations=True)
    sys.exit(0 if success else 1)
