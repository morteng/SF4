# tests/conftest.py

import pytest
import warnings
import re
import logging
import uuid
import contextlib

# Add a flag to track if freezegun is available
try:
    import freezegun
    FREEZEGUN_INSTALLED = True
except ImportError:
    FREEZEGUN_INSTALLED = False
    warnings.warn(
        "freezegun is not installed. Time-based tests will be skipped. "
        "Run `pip install -r requirements.txt` to install dependencies."
    )
    logging.warning("freezegun is not installed. Time-based tests will be skipped.")

# Add a pytest marker for freezegun-dependent tests
def pytest_configure(config):
    """Configure pytest options."""
    config.addinivalue_line(
        "markers",
        "freezegun: mark tests that require freezegun package"
    )

# Skip freezegun-dependent tests if freezegun is not installed
def pytest_collection_modifyitems(config, items):
    """Skip tests marked with 'freezegun' if freezegun is not installed."""
    if not FREEZEGUN_INSTALLED:
        skip_freezegun = pytest.mark.skip(reason="freezegun is not installed")
        for item in items:
            if "freezegun" in item.keywords:
                item.add_marker(skip_freezegun)

def verify_dependencies():
    """Verify that all required dependencies are installed."""
    missing_deps = []
    required_deps = ["freezegun", "pytest", "Flask", "flask_limiter"]  # Add other critical dependencies here

    for dep in required_deps:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)

    if missing_deps:
        missing_deps_str = ", ".join(missing_deps)
        logging.error(
            f"The following dependencies are missing: {missing_deps_str}. "
            f"Run `pip install -r requirements.txt` to install them."
        )
        pytest.fail(f"Missing dependencies: {missing_deps_str}")

def pytest_sessionstart(session):
    """Verify dependencies at the start of the test session."""
    verify_dependencies()
    if not FREEZEGUN_INSTALLED:
        logging.warning(
            "freezegun is not installed. Some tests may be skipped. "
            "Run `pip install freezegun` to install it."
        )

# Add a pytest marker for freezegun-dependent tests
def pytest_configure(config):
    """Configure pytest options."""
    config.addinivalue_line(
        "markers",
        "freezegun: mark tests that require freezegun package"
    )

from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SAWarning
from flask import url_for, current_app
from flask_wtf.csrf import generate_csrf
from app import create_app
from app.extensions import db, login_manager
from app.models.user import User
from app.models.organization import Organization
from app.models.stipend import Stipend
from app.models.tag import Tag

# Ignore SAWarnings for cleaner test output
warnings.filterwarnings("ignore", category=SAWarning)

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for the test session."""
    app = create_app('testing')
    # Add rate limiter config
    app.config['RATELIMIT_ENABLED'] = True
    app.config['RATELIMIT_STORAGE_URL'] = 'memory://'
    app.config['WTF_CSRF_ENABLED'] = True  # Enable CSRF for testing
    app.config['WTF_CSRF_SECRET_KEY'] = 'test-secret-key'  # Add CSRF secret key
    
    # Disable rate limiting for tests
    if 'limiter' in app.extensions:
        app.extensions['limiter'].enabled = False
    
    # Initialize the app with migrations
    with app.app_context():
        # Run migrations
        from flask_migrate import upgrade
        upgrade()
        
        # Initialize database and login manager
        db.session.expire_on_commit = False

        @login_manager.user_loader
        def load_user(user_id):
            user = db.session.get(User, int(user_id))
            return db.session.merge(user) if user else None
    
    yield app
    
    # Clean up database after test
    with app.app_context():
        db.session.close()
        db.drop_all()

@pytest.fixture(scope='function')
def _db(app):
    """Provide the SQLAlchemy database session for each test function."""
    with app.app_context():
        # Create all tables including audit_log
        from app.models.audit_log import AuditLog
        db.create_all()
        
        try:
            yield db
        finally:
            # Clean up
            db.session.remove()
            db.drop_all()

@pytest.fixture(scope='function')
def db_session(_db, app):
    """Provide a clean database session for each test function."""
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        
        # Create a new session using the SQLAlchemy session directly
        session = _db.session
        session.bind = connection
        
        # Ensure audit_log table exists
        from app.models.audit_log import AuditLog
        AuditLog.__table__.create(bind=connection, checkfirst=True)
        
        yield session
        
        # Cleanup
        transaction.rollback()
        connection.close()
        session.close()

@pytest.fixture(scope='function')
def client(app):
    """Provides a test client with proper session and context management."""
    with app.app_context():
        # Initialize rate limiter if present
        if 'limiter' in app.extensions:
            limiter = app.extensions['limiter']
            limiter.enabled = False
            
            # Initialize storage if needed
            if not hasattr(limiter, '_storage') or limiter._storage is None:
                limiter.init_app(app)  # Properly initialize the limiter
            
            # Reset limiter if storage is available
            if hasattr(limiter, '_storage') and limiter._storage is not None:
                try:
                    limiter.reset()
                except Exception as e:
                    app.logger.warning(f"Failed to reset rate limiter: {str(e)}")
        
        # Create test client within application context
        client = app.test_client()
        
        # Push request context
        with app.test_request_context():
            yield client

@pytest.fixture(scope='function')
def admin_user(db_session, app):
    """Provide an admin user for testing."""
    email = 'admin@example.com'
    with app.app_context():
        user = db_session.query(User).filter_by(email=email).first()
        if not user:
            user = User(username='admin', email=email, is_admin=True)
            user.set_password('password123')
            db_session.add(user)
            db_session.commit()
        else:
            # Ensure the user is merged into the current session to ensure it's not detached
            user = db_session.merge(user)
    yield user

@pytest.fixture(scope='function')
def logged_in_admin(client, admin_user, db_session):
    """Log in as the admin user."""
    with client.application.app_context():
        # Ensure admin_user is bound to the current session
        admin_user = db_session.merge(admin_user)
        db_session.refresh(admin_user)
        db_session.add(admin_user)  # Explicitly add to session
        db_session.commit()  # Commit to ensure user is persisted
    
        # Get CSRF token
        login_response = client.get(url_for('public.login'))
        csrf_token = extract_csrf_token(login_response.data)
        
        # Perform login within the same app context
        response = client.post(url_for('public.login'), data={
            'username': admin_user.username,
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        assert response.status_code == 200, "Admin login failed."
        with client.session_transaction() as session:
            assert '_user_id' in session, "Admin session not established."
            assert session['_user_id'] == str(admin_user.id)
    
    yield client
    
    # Logout after test
    with client.application.app_context():
        client.get(url_for('public.logout'))

@pytest.fixture(scope='function')
def user_data():
    return {
        'username': 'test_user',
        'email': 'test_user@example.com',
        'password': 'password123',
        'is_admin': False
    }

@pytest.fixture(scope='function')
def test_user(db_session, app):
    """Provide a test user with unique credentials."""
    with app.app_context():
        # Create unique username and email
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f'testuser_{unique_id}',
            email=f'testuser_{unique_id}@example.com',
            is_admin=False
        )
        # Set password using the proper method
        user.set_password('TestPass123!')
        db_session.add(user)
        db_session.commit()
        # Yield the user within the app context
        yield user
        # Clean up user and related records
        from app.models.audit_log import AuditLog
        from app.models.notification import Notification
        
        # Delete related audit logs and notifications
        db_session.query(AuditLog).filter_by(user_id=user.id).delete()
        db_session.query(Notification).filter_by(user_id=user.id).delete()
        
        # Delete the user
        db_session.delete(user)
        db_session.commit()

@pytest.fixture(scope='function')
def stipend_data():
    return {
        'name': 'Test Stipend',
        'summary': 'This is a test stipend.',
        'description': 'Detailed description of the test stipend.',
        'homepage_url': 'http://example.com/stipend',
        'application_procedure': 'Apply online at example.com',
        'eligibility_criteria': 'Open to all students',
        'application_deadline': datetime.strptime('2023-12-31 23:59:59', '%Y-%m-%d %H:%M:%S'),  # Convert string to datetime
        'open_for_applications': True
    }

@pytest.fixture(scope='function')
def test_stipend(db_session, stipend_data, test_organization, app):
    """Provide a test stipend."""
    with app.app_context():
        # Merge the organization into the current session
        test_organization = db_session.merge(test_organization)
        stipend_data['organization_id'] = test_organization.id
        stipend = Stipend(**stipend_data)
        db_session.add(stipend)
        db_session.commit()
        yield stipend
        # Cleanup after test
        if db_session.query(Stipend).filter_by(id=stipend.id).first():
            db_session.delete(stipend)
            db_session.commit()

@pytest.fixture(scope='function')
def organization_data():
    return {
        'name': 'Test Organization',
        'description': 'This is a test organization.',
        'homepage_url': 'http://example.com/organization'
    }

class BaseTest:
    @pytest.fixture
    def test_entity(self, db_session, app, model, data):
        """Generic fixture for test entities"""
        with app.app_context():
            entity = model(**data)
            db_session.add(entity)
            db_session.commit()
            yield entity
            db_session.delete(entity)
            db_session.commit()

@pytest.fixture(scope='function')
def test_organization(db_session, organization_data, app):
    """Provide a test organization using BaseTest."""
    base_test = BaseTest()
    yield from base_test.test_entity(db_session, app, Organization, organization_data)

@pytest.fixture(scope='function')
def tag_data():
    return {
        'name': 'Test Tag',
        'category': 'Test Category'
    }

# Helper Function
def test_required_packages():
    try:
        import flask_limiter
        assert True
    except ImportError:
        pytest.fail("Flask-Limiter is not installed")

def generate_csrf_token():
    """Generate a CSRF token for testing."""
    from flask_wtf.csrf import generate_csrf
    return generate_csrf()

def extract_csrf_token(response_data):
    """Extract CSRF token from response data."""
    try:
        decoded_data = response_data.decode('utf-8')
        # Look for CSRF token in hidden input field
        match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"', decoded_data)
        if match:
            return match.group(1)
        # Look for CSRF token in meta tag
        match = re.search(r'<meta[^>]*name="csrf-token"[^>]*content="([^"]+)"', decoded_data)
        if match:
            return match.group(1)
        # Look for CSRF token in form
        match = re.search(r'name="csrf_token"\s*value="([^"]+)"', decoded_data)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        logging.error(f"Error extracting CSRF token: {str(e)}")
        return None

def get_all_tags():
    with current_app.app_context():  # Ensure application context is set
        return Tag.query.all()

@pytest.fixture(autouse=True)
def reset_rate_limiter(app):
    """Reset the rate limiter and clear audit logs before each test."""
    with app.app_context():
        # Reset rate limiter if it exists and is initialized
        if 'limiter' in app.extensions:
            limiter = app.extensions['limiter']
            if hasattr(limiter, '_storage') and limiter._storage is not None:
                try:
                    limiter.reset()
                except Exception as e:
                    # Log but don't fail the test if reset fails
                    app.logger.warning(f"Failed to reset rate limiter: {str(e)}")
        
        # Clear audit logs and notifications
        from app.models.audit_log import AuditLog
        from app.models.notification import Notification
        try:
            AuditLog.query.delete()
            Notification.query.delete()
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error clearing audit logs: {str(e)}")
            db.session.rollback()

@pytest.fixture(scope='function')
def logged_in_client(client, test_user, app, db_session):
    """Log in as a regular user."""
    with app.app_context():
        # Initialize rate limiter if needed
        if 'limiter' in app.extensions:
            limiter = app.extensions['limiter']
            limiter.enabled = False
            
            # Ensure limiter is properly initialized
            if not hasattr(limiter, '_storage') or limiter._storage is None:
                limiter.init_app(app)  # Reinitialize if needed
            
            # Reset limiter if storage is available
            if hasattr(limiter, '_storage') and limiter._storage is not None:
                try:
                    limiter.reset()
                except Exception as e:
                    app.logger.warning(f"Failed to reset rate limiter: {str(e)}")
    
    # Ensure the test_user is bound to the current session
    db_session.add(test_user)
    db_session.commit()
    
    # Get login page and extract CSRF token
    login_response = client.get(url_for('public.login'))
    csrf_token = extract_csrf_token(login_response.data)
    
    # Submit login form
    response = client.post(url_for('public.login'), data={
        'username': test_user.username,
        'password': 'TestPass123!',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200, f"User login failed. Response: {response.data.decode('utf-8')}"
    with client.session_transaction() as session:
        assert '_user_id' in session, "User session not established."
    
    yield client
    
    # Logout after test
    client.get(url_for('public.logout'))

class BaseCRUDTest:
    """Base class for CRUD operation tests."""
    service_class = None
    model_class = None

    def test_create(self, test_data, db_session, app):
        """Test creating a new entity."""
        with app.app_context():
            service = self.service_class()
            entity = service.create(test_data)
            assert entity.id is not None
            assert isinstance(entity, self.model_class)

    def test_get_by_id(self, test_data, db_session, app):
        """Test retrieving an entity by ID."""
        with app.app_context():
            service = self.service_class()
            entity = service.create(test_data)
            retrieved_entity = service.get_by_id(entity.id)
            assert retrieved_entity.id == entity.id

    def test_update(self, test_data, db_session, app):
        """Test updating an entity."""
        with app.app_context():
            service = self.service_class()
            entity = service.create(test_data)
            updated_data = {**test_data, 'name': 'Updated Name'}
            updated_entity = service.update(entity.id, updated_data)
            assert updated_entity.name == 'Updated Name'

    def test_delete(self, test_data, db_session, app):
        """Test deleting an entity."""
        with app.app_context():
            service = self.service_class()
            entity = service.create(test_data)
            service.delete(entity.id)
            deleted_entity = service.get_by_id(entity.id)
            assert deleted_entity is None

@pytest.fixture
def form_data(app):
    """Fixture for form test data"""
    with app.app_context():
        # Clean up existing test data
        db.session.query(Tag).filter(Tag.name == "Test Tag").delete()
        db.session.query(Organization).filter(Organization.name == "Test Org").delete()
        db.session.commit()

        # Create new test data
        org = Organization(name="Test Org", description="Test Description", homepage_url="https://test.org")
        tag = Tag(name="Test Tag", category="Test Category")
        db.session.add(org)
        db.session.add(tag)
        db.session.commit()

        # Generate CSRF token inside a test request context
        with app.test_request_context():
            csrf_token = generate_csrf()

        return {
            'name': 'Test Stipend',
            'summary': 'Test summary',
            'description': 'Test description',
            'homepage_url': 'https://example.com',
            'application_procedure': 'Test procedure',
            'eligibility_criteria': 'Test criteria',
            'organization_id': org.id,
            'tags': [tag.id],
            'open_for_applications': True,
            'application_deadline': '2025-12-31 23:59:59',
            'csrf_token': csrf_token
        }

@pytest.fixture(scope='function')
def test_tag(db_session, app):
    """Provide a test tag."""
    with app.app_context():
        tag = Tag(name="TestTag", category="TestCategory")
        db_session.add(tag)
        db_session.commit()
    yield tag
    with app.app_context():
        # Merge the tag back into the session to ensure it's not detached
        tag = db_session.merge(tag)
        if db_session.query(Tag).filter_by(id=tag.id).first():
            db_session.delete(tag)
            db_session.commit()
import importlib
import pytest

def verify_dependencies():
    missing_deps = []
    for dep in ["freezegun", "Flask"]:
        try:
            importlib.import_module(dep)
        except ImportError:
            missing_deps.append(dep)
    if missing_deps:
        pytest.skip(f"Missing dependencies: {', '.join(missing_deps)}")

def pytest_sessionstart(session):
    verify_dependencies()
import subprocess
import pytest
import importlib

def verify_dependencies():
    missing_deps = []
    for dep in ["freezegun", "Flask"]:
        try:
            importlib.import_module(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"Attempting to install missing dependencies: {', '.join(missing_deps)}")
        try:
            subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
        except subprocess.CalledProcessError:
            pytest.skip(f"Missing dependencies: {', '.join(missing_deps)}")
