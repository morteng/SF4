# tests/conftest.py
import pytest
from flask import url_for  # Import url_for here
from app import create_app, db as _database  # Import db with an alias if it's already defined in the app
from app.models.user import User
from app.extensions import db, login_manager

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.config['SERVER_NAME'] = 'localhost'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'

    with app.app_context():
        # Initialize extensions
        db.init_app(app)
        login_manager.init_app(app)

        # Prevent SQLAlchemy from expiring objects after commit
        db.session.expire_on_commit = False

        from app.models.user import User  # Ensure models are imported for table creation

        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))  # Use session.get instead of query.get

        # Register blueprints
        from app.routes.admin import register_admin_blueprints
        register_admin_blueprints(app)  # For admin routes

        register_blueprints(app)        # Register other blueprints

        _database.create_all()  # Create tables

        yield app

        _database.session.remove()
        _database.drop_all()

@pytest.fixture(scope='session')
def _db(app):
    """Provide the SQLAlchemy database session for pytest-flask-sqlalchemy plugin."""
    with app.app_context():
        _database.create_all()
        yield _database  # Provide the actual database session
        _database.drop_all()
        _database.session.remove()

@pytest.fixture(scope='function')
def db(_db):
    """Provide a clean database session for each test function."""
    connection = _db.engine.connect()
    transaction = connection.begin()

    _db.session.bind = connection
    yield _db  # Provide the session

    transaction.rollback()
    connection.close()
    _database.session.remove()

@pytest.fixture(scope='function')
def admin_user(db):
    email = 'admin@example.com'
    existing_user = db.session.query(User).filter_by(email=email).first()
    if not existing_user:
        user = User(username='admin', email=email, is_admin=True)
        user.set_password('password123')  # Ensure correct password hash
        db.session.add(user)
        db.session.commit()  # Commit to persist the user
    else:
        user = existing_user
    yield user
    db.session.rollback()

@pytest.fixture(scope='function')
def client(app):
    """Provides a test client for the application."""
    return app.test_client()

@pytest.fixture
def logged_in_admin(client, admin_user):
    response = client.post(url_for('public.login'), data={
        'username': admin_user.username,
        'password': 'password123',
        'csrf_token': ''  # Add this to bypass CSRF during tests
    }, follow_redirects=True)
    assert response.status_code == 200, "Admin login failed."
    with client.session_transaction() as session:
        assert '_user_id' in session, "Admin session not established."
    yield client
