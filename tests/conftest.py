# tests/conftest.py
import pytest
from app import create_app, db as _db  # Import db with an alias if it's already defined in the app
from app.models.user import User

@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    # Add the following configurations
    app.config['SERVER_NAME'] = 'localhost'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()

@pytest.fixture(scope='function')
def admin_user(db):
    email = 'admin@example.com'
    existing_user = User.query.filter_by(email=email).first()
    if not existing_user:
        user = User(username='admin', email=email, is_admin=True)
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()
    else:
        user = existing_user
    yield user
    db.session.rollback()

@pytest.fixture(scope='function')
def db(app):
    """Create a new database session for a test."""
    with _db.engine.connect() as connection:
        transaction = connection.begin()

        _db.session.configure(bind=connection)
        yield _db.session

        # Rollback the transaction and close the session after each test
        transaction.rollback()
        _db.session.remove()
