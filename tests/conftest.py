import pytest
from flask import current_app
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import StaleDataError
from tests.utils import extract_csrf_token
from app.models import User, Stipend, Tag, Organization
from app import db
from datetime import datetime, timedelta, timezone

# Test data
@pytest.fixture
def logged_in_admin():
    # Implementation of logged_in_admin fixture
    pass

FREEZEGUN_INSTALLED = True

@pytest.fixture
def db_session():
    return db.session

@pytest.fixture
def organization_data():
    return {
        'name': 'Test Organization',
        'description': 'Test Description'
    }

@pytest.fixture
def stipend_data():
    return {
        'name': 'Test Stipend',
        'summary': 'Test Summary',
        'description': 'Test Description',
        'homepage_url': 'https://example.com',
        'application_procedure': 'Apply online',
        'eligibility_criteria': 'Open to all students',
        'application_deadline': datetime.now(timezone.utc) + timedelta(days=30),
        'open_for_applications': True
    }

@pytest.fixture
def tag_data():
    return {
        'name': 'Test Tag',
        'category': 'Academic'
    }

@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword'
    }

@pytest.fixture
def logged_in_client():
    # Implementation here
    pass

@pytest.fixture
def get_all_tags():
    # Implementation here
    pass

@pytest.fixture(scope="session")
def app():
    return current_app

@pytest.fixture(scope="session")
def client(app):
    with app.app_context():
        with app.test_client() as client:
            yield client

class BaseAdminTest:
    def __init__(self):
        self.client = None
        self.db = None
        
    def get_csrf_token(self, endpoint):
        # Implementation to get CSRF token
        pass
    
    def verify_audit_log(self, action, object_type, object_id):
        # Implementation to verify audit logs
        pass
    
    def verify_notification(self, notification_type, message):
        # Implementation to verify notifications
        pass

@pytest.fixture
def BaseCRUDTest():
    from tests.base_test_case import BaseTestCase
    return BaseTestCase

# Register custom pytest marks
def pytest_configure(config):
    config.addinivalue_line("markers", "freezegun: mark test as using freezegun")
    config.addinivalue_line("markers", "csrf: mark test as requiring CSRF token handling")
