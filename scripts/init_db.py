import os
import logging
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure paths
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from app import create_app, db
    from app.models import User, Stipend, Organization, Tag
    
    # Initialize Flask app
    app = create_app('development')
    
    # Create database tables
    with app.app_context():
        logger.info("Creating database tables...")
        db.create_all()
            
        # Add missing tags column if it doesn't exist
        from sqlalchemy import inspect, Column, JSON
        inspector = inspect(db.engine)
        if 'stipend' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('stipend')]
            if 'tags' not in columns:
                logger.info("Adding missing 'tags' column to stipend table")
                with db.engine.connect() as conn:
                    conn.execute('ALTER TABLE stipend ADD COLUMN tags JSONB')
            
        logger.info("Database tables created/updated successfully")
        
        # Create initial admin user if doesn't exist
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
            
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")
    raise
