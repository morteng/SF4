import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.factory import create_app
from app.extensions import db

from pathlib import Path

def fix_pytest_config():
    """Fix pytest configuration with proper test isolation"""
    try:
        # Create test app
        app = create_app('testing')
        
        # Update test database URI
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize extensions with proper cleanup
        with app.app_context():
            if 'sqlalchemy' not in app.extensions:
                db.init_app(app)
                db.create_all()
            
            # Create test client
            test_client = app.test_client()
        
        # Update pytest configuration with proper isolation
        pytest_config = Path('pytest.ini')
        pytest_config.write_text("""
[pytest]
testpaths = tests/
addopts = -v --cov=app --cov=scripts --cov-report=term-missing
norecursedirs = .venv .git migrations instance .pytest_cache
pythonpath = .
minversion = 7.0
python_files = test_*.py *_tests.py
python_classes = Test* *Test
python_functions = test_* *_test
filterwarnings =
    ignore::pytest.PytestConfigWarning
    ignore::DeprecationWarning
    ignore::ResourceWarning
    ignore::sqlalchemy.exc.SAWarning
    ignore::pytest.PytestUnknownMarkWarning
asyncio_mode = auto

markers =
    csrf: CSRF token related tests
    auth: Authentication related tests
    version: Version management tests
    db: Database related tests
    slow: marks tests as slow (deselect with '-m "not slow"')
""")
        
        return True
    except Exception as e:
        print(f"Pytest configuration fix failed: {str(e)}")
        return False

if __name__ == "__main__":
    fix_pytest_config()
