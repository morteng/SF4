# tests/conftest.py

import os
import sys
import uuid
import re
import logging
import warnings
import pytest
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SAWarning
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import url_for, current_app
from flask_wtf.csrf import generate_csrf
from app import create_app
from app.extensions import init_extensions, db, login_manager
from app.models.user import User
from app.models.organization import Organization
from app.models.stipend import Stipend
from app.models.tag import Tag

# Ensure the project root is in the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check if freezegun is installed
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


# -------------------------------------------------------------------
# Configure pytest markers (freezegun, auth, csrf)
# -------------------------------------------------------------------
def pytest_configure(config):
    """Configure pytest options by adding custom markers."""
    config.addinivalue_line(
        "markers",
        "freezegun: mark tests that require freezegun package"
    )
    config.addinivalue_line(
        "markers",
        "auth: mark tests related to authentication"
    )
    config.addinivalue_line(
        "markers",
        "csrf: mark tests related to CSRF protection"
    )


# -------------------------------------------------------------------
# Skip freezegun-dependent tests if freezegun is not installed
# -------------------------------------------------------------------
def pytest_collection_modifyitems(config, items):
    """Skip tests marked with 'freezegun' if freezegun is not installed."""
    if not FREEZEGUN_INSTALLED:
        skip_freezegun = pytest.mark.skip(reason="freezegun is not installed")
        for item in items:
            if "freezegun" in item.keywords:
                item.add_marker(skip_freezegun)


def pytest_sessionstart(session):
    """Verify dependencies at the start of the test session."""
    if not FREEZEGUN_INSTALLED:
        logging.warning(
            "freezegun is not installed. Some tests may be skipped. "
            "Run `pip install freezegun` to install it."
        )


# -------------------------------------------------------------------
# Application fixture
# -------------------------------------------------------------------
@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for the test session (with migrations)."""
    app = create_app("testing")
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure SQLite-specific settings
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'poolclass': 'StaticPool',
        'connect_args': {'check_same_thread': False}
    }

    # Initialize extensions
    init_extensions(app)

    # Configure rate limiter and CSRF
    app.config['RATELIMIT_ENABLED'] = False  # Disable rate limiting for tests
    app.config['RATELIMIT_STORAGE_URL'] = 'memory://'
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = 'test-secret-key'

    # Initialize the app with migrations
    with app.app_context():
        # Create migrations directory if it doesn't exist
        migrations_dir = Path('migrations')
        if not migrations_dir.exists():
            migrations_dir.mkdir()
            
        # Initialize database and run migrations
        db.create_all()
        
        # Create initial migration if needed
        from flask_migrate import Migrate
        migrate = Migrate(app, db)
        try:
            from flask_migrate import upgrade
            upgrade()
        except Exception as e:
            # If migrations fail, create the tables directly
            db.create_all()

    yield app

    # Clean up after the entire test session
    with app.app_context():
        db.session.remove()
        if hasattr(db, 'engine'):
            db.engine.dispose()
        db.drop_all()


# -------------------------------------------------------------------
# Database & Session Fixtures
# -------------------------------------------------------------------
@pytest.fixture(scope='function')
def _db(app):
    """Provide the SQLAlchemy database session for each test function."""
    with app.app_context():
        # Create all tables including audit_log
        from app.models.audit_log import AuditLog
        from app.models.stipend import Stipend
        
        # Create tables directly if migrations fail
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"Failed to create tables via migrations: {str(e)}")
            db.create_all()
        
        try:
            yield db
        finally:
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
        
        transaction.rollback()
        connection.close()
        session.close()


# -------------------------------------------------------------------
# Client Fixture
# -------------------------------------------------------------------
@pytest.fixture(scope='function')
def client(app):
    """Provides a test client with proper session, CSRF, and context management."""
    with app.app_context():
        # Initialize or disable rate limiter if present
        if 'limiter' in app.extensions:
            limiter = app.extensions['limiter']
            
            # Ensure limiter is properly initialized
            if not hasattr(limiter, '_storage'):
                limiter.init_app(app)
            
            # Reset limiter if storage is available
            if hasattr(limiter, '_storage') and limiter._storage is not None:
                try:
                    limiter._storage.reset()
                except Exception as e:
                    app.logger.warning(f"Failed to reset rate limiter: {str(e)}")
        
        # Create test client
        test_client = app.test_client()
        
        # Initialize CSRF token by making a GET request
        test_client.get('/')
        
        # Verify CSRF token is set in session
        with test_client.session_transaction() as sess:
            assert 'csrf_token' in sess, "CSRF token not set in session"
            
        yield test_client


# -------------------------------------------------------------------
# Admin User & Logged-in Admin Fixtures
# -------------------------------------------------------------------
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
            # Ensure the user is merged into the current session
            user = db_session.merge(user)
    yield user


@pytest.fixture(scope='function')
def logged_in_admin(client, admin_user, db_session):
    """Log in as the admin user."""
    with client.application.app_context():
        admin_user = db_session.merge(admin_user)
        db_session.refresh(admin_user)
        db_session.add(admin_user)
        db_session.commit()
    
        # Get CSRF token
        login_response = client.get(url_for('public.login'))
        csrf_token = extract_csrf_token(login_response.data)
        
        # Perform login
        response = client.post(
            url_for('public.login'),
            data={'username': admin_user.username,
                  'password': 'password123',
                  'csrf_token': csrf_token},
            follow_redirects=True
        )
        
        assert response.status_code == 200, "Admin login failed."
        with client.session_transaction() as sess:
            assert '_user_id' in sess, "Admin session not established."
            assert sess['_user_id'] == str(admin_user.id)
    
    yield client
    
    # Logout after test
    with client.application.app_context():
        client.get(url_for('public.logout'))


# -------------------------------------------------------------------
# Regular User Fixtures
# -------------------------------------------------------------------
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
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f'testuser_{unique_id}',
            email=f'testuser_{unique_id}@example.com',
            is_admin=False
        )
        user.set_password('TestPass123!')
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.check_password('TestPass123!')
        
        yield user
        
        # Clean up user-related records
        from app.models.audit_log import AuditLog
        from app.models.notification import Notification
        db_session.query(AuditLog).filter_by(user_id=user.id).delete()
        db_session.query(Notification).filter_by(user_id=user.id).delete()
        
        db_session.delete(user)
        db_session.commit()


@pytest.fixture(scope='function')
def logged_in_client(client, test_user, app, db_session):
    """Log in as a regular user."""
    with app.app_context():
        # Disable rate limiter if present
        if 'limiter' in app.extensions:
            limiter = app.extensions['limiter']
            limiter.enabled = False
            
            if not hasattr(limiter, '_storage') or limiter._storage is None:
                limiter.init_app(app)
            
            if hasattr(limiter, '_storage') and limiter._storage is not None:
                try:
                    limiter.reset()
                except Exception as e:
                    app.logger.warning(f"Failed to reset rate limiter: {str(e)}")
    
    db_session.add(test_user)
    db_session.commit()
    
    # Get login page and extract CSRF token
    login_response = client.get(url_for('public.login'))
    csrf_token = extract_csrf_token(login_response.data)
    
    # Submit login form
    response = client.post(
        url_for('public.login'),
        data={
            'username': test_user.username,
            'password': 'TestPass123!',
            'csrf_token': csrf_token
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200, f"User login failed. Response: {response.data.decode('utf-8')}"
    with client.session_transaction() as sess:
        assert '_user_id' in sess, "User session not established."
    
    yield client
    
    # Logout after test
    client.get(url_for('public.logout'))


# -------------------------------------------------------------------
# Organization Fixtures
# -------------------------------------------------------------------
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
        """Generic fixture for test entities."""
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


# -------------------------------------------------------------------
# Tag Fixtures
# -------------------------------------------------------------------
@pytest.fixture(scope='function')
def tag_data():
    return {
        'name': 'Test Tag',
        'category': 'Test Category'
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
        tag = db_session.merge(tag)
        if db_session.query(Tag).filter_by(id=tag.id).first():
            db_session.delete(tag)
            db_session.commit()


# -------------------------------------------------------------------
# Stipend Fixtures
# -------------------------------------------------------------------
@pytest.fixture(scope='function')
def stipend_data():
    return {
        'name': 'Test Stipend',
        'summary': 'This is a test stipend.',
        'description': 'Detailed description of the test stipend.',
        'homepage_url': 'http://example.com/stipend',
        'application_procedure': 'Apply online at example.com',
        'eligibility_criteria': 'Open to all students',
        'application_deadline': datetime.strptime('2023-12-31 23:59:59', '%Y-%m-%d %H:%M:%S'),
        'open_for_applications': True
    }


@pytest.fixture(scope='function')
def test_stipend(db_session, stipend_data, test_organization, app):
    """Provide a test stipend."""
    with app.app_context():
        test_organization = db_session.merge(test_organization)
        stipend_data['organization_id'] = test_organization.id
        stipend = Stipend(**stipend_data)
        db_session.add(stipend)
        db_session.commit()
        yield stipend
        # Cleanup
        if db_session.query(Stipend).filter_by(id=stipend.id).first():
            db_session.delete(stipend)
            db_session.commit()


# -------------------------------------------------------------------
# Rate Limiter Reset Fixture
# -------------------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_rate_limiter(app):
    """Reset the rate limiter and clear audit logs before each test."""
    with app.app_context():
        # Only attempt to reset limiter if it's properly initialized
        if 'limiter' in app.extensions:
            limiter = app.extensions['limiter']
            if hasattr(limiter, '_storage') and limiter._storage is not None:
                try:
                    limiter._storage.reset()
                except Exception as e:
                    app.logger.warning(f"Failed to reset rate limiter: {str(e)}")
        
        from app.models.audit_log import AuditLog
        from app.models.notification import Notification
        try:
            AuditLog.query.delete()
            Notification.query.delete()
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error clearing audit logs: {str(e)}")
            db.session.rollback()


# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------
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
    """Extract CSRF token from response data with improved reliability."""
    try:
        decoded_data = response_data.decode('utf-8')
        patterns = [
            r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"',
            r'<meta[^>]*name="csrf-token"[^>]*content="([^"]+)"',
            r'name="csrf_token"\s*value="([^"]+)"',
            r'csrf_token.*?value="([^"]+)"',
            r'csrf-token.*?content="([^"]+)"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, decoded_data, re.DOTALL)
            if match:
                return match.group(1)
                
        if hasattr(response_data, 'headers'):
            return response_data.headers.get('X-CSRF-Token')
            
        return None
    except Exception as e:
        logging.error(f"Error extracting CSRF token: {str(e)}")
        return None


def get_csrf_token(client, route_name=None):
    """Helper to get CSRF token for a specific route or from '/' if None."""
    if route_name:
        response = client.get(url_for(route_name))
    else:
        response = client.get('/')
    
    token = extract_csrf_token(response.data)
    if not token:
        with client.session_transaction() as sess:
            token = sess.get('csrf_token')
    return token


def login_as_admin(client, username='admin', password='admin'):
    """Helper to login as admin user."""
    client.get(url_for('public.login'))
    csrf_token = get_csrf_token(client, 'public.login')
    
    response = client.post(
        url_for('public.login'),
        data={'username': username, 'password': password, 'csrf_token': csrf_token},
        follow_redirects=True
    )
    
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert '_user_id' in sess
        assert '_fresh' in sess
    
    return response


def submit_form(client, route_name, form_data, method='POST'):
    """Helper to submit a form with CSRF token and proper headers."""
    csrf_token = get_csrf_token(client)
    if 'csrf_token' not in form_data:
        form_data['csrf_token'] = csrf_token
        
    headers = {
        'X-CSRFToken': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://localhost/'
    }
    
    if method == 'POST':
        data = form_data
        query_string = None
    else:
        data = None
        query_string = form_data
    
    client.get(url_for(route_name))  # Set up session CSRF if needed
    
    response = client.open(
        url_for(route_name),
        method=method,
        data=data,
        query_string=query_string,
        headers=headers,
        follow_redirects=True
    )
    
    if response.status_code == 302:
        with client.session_transaction() as sess:
            if '_flashes' in sess:
                flash_messages = sess['_flashes']
                assert not any('CSRF' in msg for _, msg in flash_messages), \
                    "CSRF validation failed in form submission"
    
    return response


def get_all_tags():
    with current_app.app_context():
        return Tag.query.all()


# -------------------------------------------------------------------
# Example Parametrized CSRF Test
# -------------------------------------------------------------------
@pytest.mark.parametrize('route_name,method', [
    ('admin.stipend.create', 'POST'),
    ('admin.stipend.edit', 'POST'),
    ('admin.stipend.delete', 'POST')
])
def test_csrf_validation(client, logged_in_admin, route_name, method):
    """Test CSRF validation for protected routes."""
    response = client.open(
        url_for(route_name),
        method=method,
        data={},
        follow_redirects=True
    )
    
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert '_flashes' in sess
        flash_messages = sess['_flashes']
        assert any('CSRF token is missing' in msg for _, msg in flash_messages)


# -------------------------------------------------------------------
# CRUD Base Class
# -------------------------------------------------------------------
class BaseCRUDTest:
    """Base class for CRUD operation tests."""
    service_class = None
    model_class = None

    def test_create(self, test_data, db_session, app):
        with app.app_context():
            service = self.service_class()
            entity = service.create(test_data)
            assert entity.id is not None
            assert isinstance(entity, self.model_class)

    def test_get_by_id(self, test_data, db_session, app):
        with app.app_context():
            service = self.service_class()
            entity = service.create(test_data)
            retrieved_entity = service.get_by_id(entity.id)
            assert retrieved_entity.id == entity.id

    def test_update(self, test_data, db_session, app):
        with app.app_context():
            service = self.service_class()
            entity = service.create(test_data)
            updated_data = {**test_data, 'name': 'Updated Name'}
            updated_entity = service.update(entity.id, updated_data)
            assert updated_entity.name == 'Updated Name'

    def test_delete(self, test_data, db_session, app):
        with app.app_context():
            service = self.service_class()
            entity = service.create(test_data)
            service.delete(entity.id)
            deleted_entity = service.get_by_id(entity.id)
            assert deleted_entity is None


# -------------------------------------------------------------------
# Form Data Fixture
# -------------------------------------------------------------------
@pytest.fixture
def form_data(app):
    """Fixture for form test data."""
    with app.app_context():
        db.session.query(Tag).filter(Tag.name == "Test Tag").delete()
        db.session.query(Organization).filter(Organization.name == "Test Org").delete()
        db.session.commit()

        org = Organization(name="Test Org", description="Test Description", homepage_url="https://test.org")
        tag = Tag(name="Test Tag", category="Test Category")
        db.session.add(org)
        db.session.add(tag)
        db.session.commit()

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


# -------------------------------------------------------------------
# Test Blueprint Registration Fixture
# -------------------------------------------------------------------
@pytest.fixture
def test_blueprint_registration(app):
    """Test blueprint registration."""
    with app.app_context():
        from app.routes.admin import register_admin_blueprints
        register_admin_blueprints(app)
        
        assert 'admin' in app.blueprints
        assert 'admin.stipend' in app.blueprints
        assert 'admin.dashboard' in app.blueprints
        
        registered_routes = [rule.endpoint for rule in app.url_map.iter_rules()]
        assert 'admin.stipend.create' in registered_routes
        assert 'admin.dashboard.dashboard' in registered_routes
