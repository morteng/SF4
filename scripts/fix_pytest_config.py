import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.factory import create_app
from app.extensions import db

from pathlib import Path

def fix_pytest_config():
    """Fix pytest configuration"""
    try:
        # Create test app
        app = create_app('testing')
        
        # Update test database URI
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize extensions if not already initialized
        if 'sqlalchemy' not in app.extensions:
            db.init_app(app)
        
        # Create test client
        with app.app_context():
            db.create_all()
            test_client = app.test_client()
        
        # Update pytest configuration
        pytest_config = Path('pytest.ini')
        if not pytest_config.exists():
            pytest_config.write_text("""
[pytest]
testpaths = tests/
addopts = -v --cov=app --cov=scripts --cov-report=term-missing
""")
        
        return True
    except Exception as e:
        print(f"Pytest configuration fix failed: {str(e)}")
        return False

if __name__ == "__main__":
    fix_pytest_config()
