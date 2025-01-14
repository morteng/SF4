import os
import logging
from pathlib import Path
import sys
from sqlalchemy import text, inspect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure paths
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def add_tags_column():
    """Add tags column to stipend table with proper error handling"""
    try:
        from app import db
        inspector = inspect(db.engine)
        if 'stipend' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('stipend')]
            if 'tags' not in columns:
                logger.info("Adding missing 'tags' column to stipend table")
                with db.engine.connect() as conn:
                    stmt = text("ALTER TABLE stipend ADD COLUMN tags JSONB")
                    conn.execute(stmt)
                    conn.commit()
                    logger.info("Successfully added tags column")
                    return True
        return False
    except Exception as e:
        logger.error(f"Failed to add tags column: {str(e)}")
        return False

def recreate_tables():
    """Recreate all database tables as a fallback"""
    try:
        from app import db
        logger.info("Recreating database tables...")
        db.drop_all()
        db.create_all()
        logger.info("Successfully recreated database tables")
        return True
    except Exception as e:
        logger.error(f"Failed to recreate tables: {str(e)}")
        return False

def create_admin_user():
    """Create initial admin user if it doesn't exist"""
    try:
        from app import db
        from app.models import User
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password='password',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("Created initial admin user")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        return False

def main():
    try:
        from app import create_app, db
        
        # Initialize Flask app
        app = create_app('development')
        
        with app.app_context():
            # First try adding the tags column
            if not add_tags_column():
                # If that fails, recreate all tables
                if not recreate_tables():
                    raise RuntimeError("Failed to initialize database schema")
            
            # Create admin user
            create_admin_user()
            
            logger.info("Database initialization completed successfully")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
