import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/tests.log'),
        logging.StreamHandler()
    ]
)

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
# Add app directory to Python path
app_dir = str(Path(__file__).parent.parent / 'app')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Set test environment variables
os.environ['FLASK_ENV'] = 'testing'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
os.environ['ADMIN_USERNAME'] = 'testadmin'
os.environ['ADMIN_EMAIL'] = 'test@example.com'
os.environ['ADMIN_PASSWORD'] = 'TestPassword123!'
os.environ['SECRET_KEY'] = 'TestSecretKey1234567890!@#$%^&*()'

print("Test environment configured successfully")
