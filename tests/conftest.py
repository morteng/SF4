import sys
from pathlib import Path
import pytest  # Add this import

# Get the project root directory
root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

from app import create_app

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    return app
