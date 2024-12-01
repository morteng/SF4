# tests/conftest.py
import pytest
from app import create_app
from app.config import TestingConfig  # Import the config class directly
from app.extensions import db as _db  # Ensure correct import
from app.models.user import User
from app.extensions import login_manager

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')  # Pass 'testing' as a string
    with app.app_context():
        _db.create_all()
    yield app
    with app.app_context():
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    with app.app_context():
        _db.create_all()
    yield _db
    with app.app_context():
        _db.drop_all()

@pytest.fixture
def session(db):
    db.session.begin_nested()
    yield db.session
    db.session.rollback()

@pytest.fixture
def logged_in_client(client, db_session):
    # Create a test user
    user = User(username='testuser', email='test@example.com', is_admin=True)
    user.set_password('testpassword')
    db_session.add(user)
    db_session.commit()

    # Log in the user
    with client.session_transaction() as session:
        user_obj = User.query.filter_by(username='testuser').first()
        login_manager.login_user(user_obj)
        session['user_id'] = user_obj.id
        session['_user_id'] = str(user_obj.get_id())  # Add this line

    return client
