# tests/conftest.py
import pytest
from flask import url_for
from app import create_app
from app.extensions import db, login_manager  # Correct imports
from app.models.user import User

@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test function."""
    app = create_app('testing')  # 'create_app' already sets testing configs

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
