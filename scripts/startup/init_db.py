import logging
from pathlib import Path
from alembic import command
from alembic.config import Config
try:
    from app import db
except ImportError:
    import sys
    from pathlib import Path
    # Add both app and scripts directories to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # Project root
    sys.path.insert(0, str(Path(__file__).parent.parent))  # Scripts dir
    from app import db

logger = logging.getLogger(__name__)

def initialize_database(validate_schema=False):
    """Initialize database schema and run migrations"""
    try:
        # Add project root to sys.path
        import sys
        import os
        from pathlib import Path
        project_root = str(Path(__file__).parent.parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Configure logging
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Ensure debug mode is disabled
        os.environ['FLASK_DEBUG'] = '0'
        if not configure_paths():
            raise RuntimeError("Failed to configure paths")
            
        # Verify database file exists
        db_path = Path('instance/site.db')
        
        # Ensure debug mode is disabled
        os.environ['FLASK_DEBUG'] = '0'
        if not db_path.exists():
            logger.info("Creating new database file")
            db_path.parent.mkdir(exist_ok=True, parents=True)
            db_path.touch(mode=0o600)  # Set secure permissions
            
        # Create required tables with application context
        from app import create_app
        app = create_app()
        with app.app_context():
            from app.models import Stipend, Tag, Organization, User
            db.create_all()
        
        # Verify required tables exist
        required_tables = ['stipend', 'tag', 'organization', 'user']
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        for table in required_tables:
            if table not in existing_tables:
                logger.error(f"Missing required table: {table}")
                return False
            
        # Run Alembic migrations
        alembic_cfg = Config("migrations/alembic.ini")
        command.upgrade(alembic_cfg, 'head')
        
        # Validate schema if requested
        if validate_schema:
            from scripts.verify_db_schema import validate_schema
            if not validate_schema():
                logger.error("Schema validation failed")
                return False
                
        logger.info("Database initialization completed")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if initialize_database():
        print("Database initialization successful")
        exit(0)
    else:
        print("Database initialization failed")
        exit(1)
