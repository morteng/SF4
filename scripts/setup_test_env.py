import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Set test environment variables
os.environ['FLASK_ENV'] = 'testing'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
os.environ['ADMIN_USERNAME'] = 'testadmin'
os.environ['ADMIN_EMAIL'] = 'test@example.com'
os.environ['ADMIN_PASSWORD'] = 'TestPassword123!'
os.environ['SECRET_KEY'] = 'TestSecretKey1234567890!@#$%^&*()'

print("Test environment configured successfully")
