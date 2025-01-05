import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic import command
from alembic.config import Config
from app import create_app

def validate_schema():
    """Validate database schema against migrations"""
    try:
        app = create_app('testing')
        with app.app_context():
            config = Config('migrations/alembic.ini')
            command.upgrade(config, 'head')
            print("Schema validation successful")
            return True
    except Exception as e:
        print(f"Schema validation failed: {str(e)}")
        return False

if __name__ == "__main__":
    validate_schema()
