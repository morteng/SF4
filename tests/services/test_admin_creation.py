import pytest
import os
from app.models.user import User
from app import db
from scripts.startup.init_admin import initialize_admin_user

@pytest.fixture
def init_test_db():
    """Initialize test database"""
    db.create_all()
    yield
    db.drop_all()

def test_admin_user_creation(init_test_db):
    """Test admin user initialization"""
    # Verify no admin users exist
    assert User.query.filter_by(is_admin=True).count() == 0
    
    # Initialize admin user
    assert initialize_admin_user() is True
    
    # Verify admin user was created
    admin = User.query.filter_by(is_admin=True).first()
    assert admin is not None
    assert admin.username == os.getenv('ADMIN_USERNAME')
    assert admin.email == os.getenv('ADMIN_EMAIL')
