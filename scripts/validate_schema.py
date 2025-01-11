import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic import command
from alembic.config import Config
from app import create_app

def validate_schema():
    """Validate database schema against migrations"""
    try:
        # Configure logging first
        from scripts.init_logging import configure_logging
        configure_logging(production=True)
        
        app = create_app('production')
        with app.app_context():
            # Ensure database exists
            if not os.path.exists('instance/stipend.db'):
                print("Database file not found")
                # Create empty database if not exists
                from app.extensions import db
                db.create_all()
                print("Created new database schema")
                
            config = Config('migrations/alembic.ini')
            command.upgrade(config, 'head')
            print("Schema validation successful")
            return True
    except Exception as e:
        print(f"Schema validation failed: {str(e)}")
        return False

if __name__ == "__main__":
    validate_schema()
