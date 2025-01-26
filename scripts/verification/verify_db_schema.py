import os
import logging
import sys
from pathlib import Path
from sqlalchemy import inspect, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

def configure_paths():
    """Configure project paths with proper error handling."""
    try:
        project_root = str(Path(__file__).resolve().parent.parent.parent)
        logger.info(f"Calculated project_root: {project_root}")
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        app_dir = str(Path(project_root) / 'app')
        logger.info(f"Calculated app_dir: {app_dir}")
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

def verify_db_schema(validate_relations=False, validate_required_fields=True, test_config=None, emergency_create=False):
    """Enhanced schema validation with emergency table creation"""
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from app import create_app
    app = create_app()
    with app.app_context():
        if test_config:
            from flask import current_app
            if not current_app:
                app = create_app(config=test_config)
                app.app_context().push()

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

        # Validate critical columns
        user_columns = [col['name'].lower() for col in inspector.get_columns('user')]
        required_columns = {'confirmed_at', 'last_failed_login', 'is_admin', 'email', 'password_hash'}
        missing_cols = required_columns - set(user_columns)
        if missing_cols:
            logger.error(f"Missing security columns in user table: {', '.join(missing_cols)}")
            logger.info("Run 'alembic upgrade head' to apply missing migrations")
            return False

        # Define expected schema
        expected_schema = {
            'user': ['id', 'username', 'email', 'password_hash', 'is_admin',
                    'is_active', 'created_at', 'updated_at', 'confirmed_at'],
            'stipend': ['id', 'name', 'tags'],
            'organization': ['id', 'name', 'description'],
            'tag': ['id', 'name']
        }

        actual_tables = inspector.get_table_names()

        # Verify all expected tables exist
        missing_tables = set(expected_schema.keys()) - set(actual_tables)
        if missing_tables:
            logger.error(f"Missing tables: {', '.join(missing_tables)}")
            return False

        # Verify table columns with detailed error reporting
        for table, expected_columns in expected_schema.items():
            actual_columns = [col['name'] for col in inspector.get_columns(table)]

            missing_columns = set(expected_columns) - set(actual_columns)

            if missing_columns:
                if table == 'stipend' and 'tags' in missing_columns:
                    logger.error("Critical schema issue: Missing 'tags' column in stipend table")
                    logger.info("Attempting to fix schema automatically...")
                    try:
                        with engine.connect() as conn:
                            stmt = text("ALTER TABLE stipend ADD COLUMN tags JSONB")
                            conn.execute(stmt)
                            conn.commit()
                            logger.info("Successfully added tags column")
                            return verify_db_schema(validate_relations, validate_required_fields)
                    except Exception as e:
                        logger.error(f"Failed to automatically fix schema: {str(e)}")
                        logger.info("Manual repair suggestion: Run 'flask db migrate' and 'flask db upgrade'")

                logger.error(f"Missing columns in {table}: {', '.join(missing_columns)}")
                logger.info(f"Expected columns for {table}: {', '.join(expected_columns)}")
                logger.info(f"Actual columns found: {', '.join(actual_columns)}")
                return False

            if table == 'stipend':
                for col in inspector.get_columns(table):
                    if col['name'] == 'tags':
                        # Check for either JSONB or JSON type
                        if col['type'].__class__.__name__ not in ['JSONB', 'JSON']:
                            logger.error(f"Invalid type for tags column - expected JSONB/JSON, got {col['type'].__class__.__name__}")
                            return False

        if validate_required_fields:
            stipend_columns = inspector.get_columns('stipend')
            name_col = next((col for col in stipend_columns if col['name'] == 'name'), None)
            if not name_col or name_col.get('nullable', True):
                logger.error("Stipend name must be a required field")
                return False

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
    success = verify_db_schema(validate_relations=True)
    sys.exit(0 if success else 1)
