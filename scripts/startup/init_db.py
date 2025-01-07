import logging
from pathlib import Path
from alembic import command
from alembic.config import Config
try:
    from app import db
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from app import db

logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database schema and run migrations"""
    try:
        # Verify database file exists
        db_path = Path('instance/site.db')
        if not db_path.exists():
            logger.info("Creating new database file")
            db_path.parent.mkdir(exist_ok=True)
            db_path.touch()
            
        # Run Alembic migrations
        alembic_cfg = Config("migrations/alembic.ini")
        command.upgrade(alembic_cfg, 'head')
        
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
