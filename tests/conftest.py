# tests/conftest.py

import pytest
import warnings
import re
from datetime import datetime
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

@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test function."""
    app = create_app('testing')  # Use 'testing' here, not TestConfig
    app.config['WTF_CSRF_ENABLED'] = True  # Enable CSRF for testing
    app.config['WTF_CSRF_SECRET_KEY'] = 'test-secret-key'  # Add CSRF secret key

    with app.app_context():
        db.session.expire_on_commit = False

        @login_manager.user_loader
        def load_user(user_id):
            user = db.session.get(User, int(user_id))
            return db.session.merge(user) if user else None

        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def _db(app):
    """Provide the SQLAlchemy database session for each test function."""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()
        db.session.remove()

@pytest.fixture(scope='function')
def db_session(_db, app):
    """Provide a clean database session for each test function."""
    connection = _db.engine.connect()
    transaction = connection.begin()
    _db.session.bind = connection

    with app.app_context():
        yield _db.session
        transaction.rollback()
        connection.close()
        _db.session.remove()

@pytest.fixture(scope='function')
def client(app):
    """Provides a test client for the application."""
    return app.test_client()

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
def logged_in_admin(client, admin_user, db_session, app):
    """Log in as the admin user."""
    with client.application.test_request_context():
        # Merge the admin_user into the current session to ensure it's not detached
        admin_user = db_session.merge(admin_user)
        
        login_response = client.get(url_for('public.login'))
        csrf_token = extract_csrf_token(login_response.data)

        response = client.post(url_for('public.login'), data={
            'username': admin_user.username,
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200, "Admin login failed."
        with client.session_transaction() as session:
            assert '_user_id' in session, "Admin session not established."
    yield client

@pytest.fixture(scope='function')
def user_data():
    return {
        'username': 'test_user',
        'email': 'test_user@example.com',
        'password': 'password123',
        'is_admin': False
    }

@pytest.fixture(scope='function')
def test_user(db_session, user_data, app):
    """Provide a test user."""
    with app.app_context():
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            is_admin=user_data['is_admin']
        )
        user.set_password(user_data['password'])
        db_session.add(user)
        db_session.commit()
    yield user
    with app.app_context():
        # Merge the user back into the session to ensure it's not detached
        user = db_session.merge(user)
        if db_session.query(User).filter_by(id=user.id).first():
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

def extract_csrf_token(response_data):
    match = re.search(r'name="csrf_token".*?value="(.+?)"', response_data.decode('utf-8'))
    return match.group(1) if match else "dummy_csrf_token"

def get_all_tags():
    with current_app.app_context():  # Ensure application context is set
        return Tag.query.all()

@pytest.fixture(scope='function')
def logged_in_client(client, test_user, app, db_session):
    """Log in as a regular user."""
    with client.application.test_request_context():
        # Ensure the test_user is bound to the current session
        db_session.add(test_user)
        db_session.commit()

        login_response = client.get(url_for('public.login'))
        csrf_token = extract_csrf_token(login_response.data)

        response = client.post(url_for('public.login'), data={
            'username': test_user.username,
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200, "User login failed."
        with client.session_transaction() as session:
            assert '_user_id' in session, "User session not established."
    yield client

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
