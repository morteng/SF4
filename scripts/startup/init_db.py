import logging
import os
import time
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

def initialize_database(validate_schema=False, production=False, retry=3):
    """Initialize database with production context support"""
    logger = logging.getLogger(__name__)
    try:
        # Add project root to path
        project_root = str(Path(__file__).parent.parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Configure paths
        from scripts.path_config import configure_paths
        if not configure_paths(production=production):
            raise RuntimeError("Failed to configure paths")
            
        # Verify imports work
        import app
        from app.models import Stipend, Tag, Organization, User
        
        # Create application context
        from app import create_app
        app = create_app()
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Verify required tables exist
            required_tables = ['stipend', 'tag', 'organization', 'user']
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            for table in required_tables:
                if table not in existing_tables:
                    logger.error(f"Missing required table: {table}")
                    return False
            
        # Configure logging
        from scripts.init_logging import configure_logging
        configure_logging(production=production)
        logger = logging.getLogger(__name__)
            
        # Configure logging first
        from scripts.init_logging import configure_logging
        configure_logging(production=production)
        logger = logging.getLogger(__name__)
            
        # Configure paths
        from scripts.path_config import configure_paths
        if not configure_paths(production=production):
            logger.error("Failed to configure paths")
            return False
            
        # Import app with proper context
        from app import create_app
        app = create_app()
        with app.app_context():
            # Create required tables
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
            
        # Configure logging
        from scripts.init_logging import configure_logging
        configure_logging()
        logger = logging.getLogger(__name__)
        
        # Create and configure test app
        from app.factory import create_app
        app = create_app('testing')
        
        # Push application context
        app_context = app.app_context()
        app_context.push()
            
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
            
            # Retry logic for table creation
            for attempt in range(retry):
                try:
                    db.create_all()
                    break
                except Exception as e:
                    if attempt == retry - 1:
                        raise
                    time.sleep(1)
        
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
