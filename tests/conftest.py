# tests/conftest.py

import pytest
import warnings
import re
import logging
import uuid
import contextlib
from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SAWarning
from flask import url_for, current_app
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
    app.config['WTF_CSRF_ENABLED'] = True  # Enable CSRF for testing
    app.config['WTF_CSRF_SECRET_KEY'] = 'test-secret-key'  # Add CSRF secret key
    
    # Disable rate limiting for tests
    if 'limiter' in app.extensions:
        app.extensions['limiter'].enabled = False
    
    # Register blueprints explicitly for testing
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # Initialize database and login manager in app context
    with app.app_context():
        db.session.expire_on_commit = False

        @login_manager.user_loader
        def load_user(user_id):
            user = db.session.get(User, int(user_id))
            return db.session.merge(user) if user else None

        # Create all database tables
        db.create_all()
    
    yield app
    
    # Clean up database after test
    with app.app_context():
        db.session.close()
        db.drop_all()

@pytest.fixture(scope='function')
def _db(app):
    """Provide the SQLAlchemy database session for each test function."""
    with app.app_context():
        yield db

@pytest.fixture(scope='function')
def db_session(_db, app):
    """Provide a clean database session for each test function."""
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        
        # Create a new session using the SQLAlchemy session directly
        session = _db.session
        session.bind = connection
        
        yield session
        
        # Cleanup
        transaction.rollback()
        connection.close()
        session.close()

@pytest.fixture(scope='function')
def client(app):
    """Provides a test client for the application with proper context management."""
    # Ensure rate limiting is disabled
    if hasattr(app, 'extensions') and 'limiter' in app.extensions:
        limiter = app.extensions['limiter']
        limiter.enabled = False
        limiter.reset()
    
    # Create a new test client
    client = app.test_client()
    
    # Create and push a new application context
    app_ctx = app.app_context()
    app_ctx.push()
    
    # Create and push a new request context
    req_ctx = app.test_request_context()
    req_ctx.push()
    
    yield client
    
    # Clean up contexts in reverse order
    req_ctx.pop()
    app_ctx.pop()

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
    # Ensure admin_user is bound to the current session
    with client.application.app_context():
        admin_user = db_session.merge(admin_user)
        db_session.refresh(admin_user)
    
    # Get CSRF token
    login_response = client.get(url_for('public.login'))
    csrf_token = extract_csrf_token(login_response.data)
    
    # Perform login
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

@pytest.fixture(scope='function')
def test_organization(db_session, organization_data, app):
    """Provide a test organization."""
    with app.app_context():
        organization = Organization(**organization_data)
        db_session.add(organization)
        db_session.commit()
        # Yield the organization within the app context
        yield organization
        # Cleanup within the same app context
        organization = db_session.merge(organization)
        if db_session.query(Organization).filter_by(id=organization.id).first():
            db_session.delete(organization)
            db_session.commit()

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
        # Reset rate limiter
        limiter = app.extensions.get("limiter")
        if limiter and hasattr(limiter, 'reset'):
            limiter.reset()
        
        # Clear audit logs and notifications
        from app.models.audit_log import AuditLog
        from app.models.notification import Notification
        AuditLog.query.delete()
        Notification.query.delete()
        db.session.commit()

@pytest.fixture(scope='function')
def logged_in_client(client, test_user, app, db_session):
    """Log in as a regular user."""
    # Ensure rate limiting is disabled
    if hasattr(app, 'extensions') and 'limiter' in app.extensions:
        limiter = app.extensions['limiter']
        limiter.enabled = False
        limiter.reset()
    
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
