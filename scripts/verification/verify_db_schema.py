import logging
import sys
from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

logger = logging.getLogger(__name__)

def verify_foreign_keys():
    """Verify foreign key relationships in the database"""
    try:
        from app import db
        inspector = inspect(db.engine)
        
        # Verify foreign key constraints
        for table in inspector.get_table_names():
            fks = inspector.get_foreign_keys(table)
            if not fks:
                continue
                
            for fk in fks:
                if not fk.get('constrained_columns'):
                    logger.error(f"Invalid foreign key in {table}")
                    return False
                    
        return True
    except Exception as e:
        logger.error(f"Foreign key verification failed: {str(e)}")
        return False

def validate_schema(validate_relations=False, validate_required_fields=False):
    """Validate database schema against expected structure
    Args:
        validate_relations (bool): Whether to validate foreign key relationships
        validate_required_fields (bool): Verify only stipend name is required
    """
    try:
        # Configure paths first
        from scripts.path_config import configure_paths
        if not configure_paths():
            raise RuntimeError("Failed to configure paths")
            
        # Get expected tables from models
        expected_tables = {
            'user': ['id', 'username', 'email', 'password_hash'],
            'stipend': ['id', 'name', 'description', 'tags'],
            'organization': ['id', 'name', 'description'],
            'tag': ['id', 'name']
        }
        
        # Add project root to Python path
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Add app directory explicitly
        app_dir = str(Path(project_root) / 'app')
        if app_dir not in sys.path:
            sys.path.insert(0, app_dir)
            
        # Verify imports
        try:
            from app import db
        except ImportError as e:
            logger.error(f"Import error: {str(e)}")
            logger.error(f"Current sys.path: {sys.path}")
            return False
            
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
                
        # Verify required fields for stipends
        if validate_required_fields:
            stipend_columns = inspector.get_columns('stipend')
            
            # Verify only name is required
            name_col = next((col for col in stipend_columns if col['name'] == 'name'), None)
            if not name_col or name_col.get('nullable', True):
                logger.error("Stipend name must be required field")
                return False
                
            # Verify other fields are optional
            optional_fields = ['description', 'tags', 'organization_id']
            for col in stipend_columns:
                if col['name'] in optional_fields and not col.get('nullable', True):
                    logger.error(f"Field {col['name']} should be optional")
                    return False
                
            # Verify other fields are optional
            optional_fields = ['description', 'tags', 'organization_id']
            for col in stipend_columns:
                if col['name'] in optional_fields and not col.get('nullable', True):
                    logger.error(f"Field {col['name']} should be optional")
                    return False
                
        # Verify foreign key relationships
        if validate_relations:
            if not verify_foreign_keys():
                logger.error("Foreign key validation failed")
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
        # Configure paths first
        from scripts.path_config import configure_paths
        if not configure_paths():
            raise RuntimeError("Failed to configure paths")
            
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
