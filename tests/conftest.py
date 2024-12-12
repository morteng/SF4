import warnings
from sqlalchemy.exc import SAWarning
warnings.filterwarnings("ignore", category=SAWarning)

import pytest
from flask import url_for
from app import create_app
from app.extensions import db, login_manager
from app.models.user import User
from app.models.organization import Organization
from datetime import datetime


@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test function."""
    app = create_app('testing')

    with app.app_context():
        # Prevent SQLAlchemy from expiring objects after commit
        db.session.expire_on_commit = False

        @login_manager.user_loader
        def load_user(user_id):
            user = db.session.get(User, int(user_id))
            if user:
                user = db.session.merge(user)
            return user

        # Create all tables
        db.create_all()

        yield app

        # Teardown: Remove session and drop all tables
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def _db(app):
    """Provide the SQLAlchemy database session for each test function."""
    with app.app_context():
        db.create_all()
        yield db  # Provide the actual database session
        db.drop_all()
        db.session.remove()

@pytest.fixture(scope='function')
def db_session(_db):
    """Provide a clean database session for each test function."""
    connection = _db.engine.connect()
    transaction = connection.begin()

    _db.session.bind = connection
    yield _db.session  # Provide the session

    transaction.rollback()
    connection.close()
    _db.session.remove()

@pytest.fixture(scope='function')
def admin_user(db_session):
    email = 'admin@example.com'
    existing_user = db_session.query(User).filter_by(email=email).first()
    if not existing_user:
        user = User(username='admin', email=email, is_admin=True)
        user.set_password('password123')  # Ensure correct password hash
        db_session.add(user)
        db_session.commit()  # Commit to persist the user
    else:
        user = existing_user
    yield user
    db_session.rollback()

@pytest.fixture(scope='function')
def client(app):
    """Provides a test client for the application."""
    return app.test_client()

@pytest.fixture
def logged_in_admin(client, admin_user):
    response = client.post(url_for('public.login'), data={
        'username': admin_user.username,
        'password': 'password123',
        'csrf_token': ''  # Bypass CSRF for testing purposes
    }, follow_redirects=True)
    assert response.status_code == 200, "Admin login failed."
    with client.session_transaction() as session:
        assert '_user_id' in session, "Admin session not established."
    yield client

@pytest.fixture(scope='function')
def legacy_db(db_session):
    """Alias fixture for db_session to support legacy tests."""
    return db_session

@pytest.fixture
def stipend_data():
    """Provide test data for stipends."""
    return {
        'name': 'Test Stipend',
        'summary': 'This is a test stipend.',
        'description': 'Detailed description of the test stipend.',
        'homepage_url': 'http://example.com/stipend',
        'application_procedure': 'Apply online at example.com',
        'eligibility_criteria': 'Open to all students',
        'application_deadline': '2023-12-31 23:59:59',
        'open_for_applications': True
    }

@pytest.fixture
def test_stipend(db_session):
    """Provide a test stipend for use in tests."""
    from app.models.stipend import Stipend
    stipend = Stipend(
        name='Test Stipend',
        summary='This is a test stipend.',
        description='Detailed description of the test stipend.',
        homepage_url='http://example.com/stipend',
        application_procedure='Apply online at example.com',
        eligibility_criteria='Open to all students',
        application_deadline=datetime(2023, 12, 31, 23, 59, 59),
        open_for_applications=True
    )
    db_session.add(stipend)
    db_session.commit()
    yield stipend
    db_session.delete(stipend)
    db_session.commit()

@pytest.fixture
def organization_data():
    """Provide test data for organizations."""
    return {
        'name': 'Test Organization',
        'description': 'This is a test organization.',
        'homepage_url': 'http://example.com/organization'
    }

@pytest.fixture
def test_organization(db_session):
    """Provide a test organization for use in tests."""
    organization = Organization(
        name='Test Organization',
        description='This is a test organization.',
        homepage_url='http://example.com/organization'
    )
    db_session.add(organization)
    db_session.commit()
    yield organization
    if db_session.is_active:
        db_session.rollback()  # Ensure no pending changes
    db_session.expunge_all()  # Detach all objects to clean up session state
