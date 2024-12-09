# tests/conftest.py
import pytest
from app import create_app, db as database  # Import db with an alias if it's already defined in the app
from app.models.user import User

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['SERVER_NAME'] = 'localhost'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

    with app.app_context():
        database.create_all()
        yield app
        database.session.remove()
        database.drop_all()

@pytest.fixture(scope='module')
def client(app, _db):
    """Create a test client for the Flask application."""
    return app.test_client()

@pytest.fixture(scope='function')
def admin_user(db):
    email = 'admin@example.com'
    existing_user = db.session.query(User).filter_by(email=email).first()
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
def db(_db):
    """Provide a transactional database session for the tests."""
    connection = _db.engine.connect()
    transaction = connection.begin()

    database.session.bind = connection
    yield database

    transaction.rollback()
    connection.close()
    database.session.remove()

