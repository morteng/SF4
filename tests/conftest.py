import pytest
import warnings
import re
from datetime import datetime
from sqlalchemy.exc import SAWarning
from flask import url_for
from app import create_app
from app.extensions import db, login_manager
from app.models.user import User
from app.models.organization import Organization
from app.models.stipend import Stipend

# Ignore SAWarnings for cleaner test output
warnings.filterwarnings("ignore", category=SAWarning)

@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test function."""
    app = create_app('testing')

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
def db_session(_db):
    """Provide a clean database session for each test function."""
    connection = _db.engine.connect()
    transaction = connection.begin()
    _db.session.bind = connection
    yield _db.session
    transaction.rollback()
    connection.close()
    _db.session.remove()

@pytest.fixture(scope='function')
def client(app):
    """Provides a test client for the application."""
    return app.test_client()

@pytest.fixture(scope='function')
def admin_user(db_session):
    """Provide an admin user for testing."""
    email = 'admin@example.com'
    user = db_session.query(User).filter_by(email=email).first()
    if not user:
        user = User(username='admin', email=email, is_admin=True)
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()
    yield user
    db_session.rollback()

@pytest.fixture(scope='function')
def logged_in_admin(client, admin_user):
    """Log in as the admin user."""
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
def test_user(db_session, user_data):
    """Provide a test user."""
    user = User(
        username=user_data['username'],
        email=user_data['email'],
        is_admin=user_data['is_admin']
    )
    user.set_password(user_data['password'])
    db_session.add(user)
    db_session.commit()
    yield user
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
        'application_deadline': '2023-12-31 23:59:59',  # Keep as string
        'open_for_applications': True
    }

@pytest.fixture(scope='function')
def test_stipend(db_session, stipend_data):
    """Provide a test stipend."""
    stipend_data['application_deadline'] = datetime.strptime(stipend_data['application_deadline'], '%Y-%m-%d %H:%M:%S')  # Convert to datetime here
    stipend = Stipend(**stipend_data)
    db_session.add(stipend)
    db_session.commit()
    yield stipend
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
def test_organization(db_session, organization_data):
    """Provide a test organization."""
    organization = Organization(**organization_data)
    db_session.add(organization)
    db_session.commit()
    yield organization
    db_session.delete(organization)
    db_session.commit()

# Helper Function
def extract_csrf_token(response_data):
    match = re.search(r'name="csrf_token".*?value="(.+?)"', response_data.decode('utf-8'))
    return match.group(1) if match else "dummy_csrf_token"

@pytest.fixture(scope='function')
def logged_in_client(client, test_user):
    """Log in as a regular user."""
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
