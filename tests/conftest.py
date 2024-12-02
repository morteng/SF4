import pytest
import logging
from app import create_app
from app.extensions import db
from flask_login import login_user
from app.models.user import User

@pytest.fixture(scope='module')
def app():
    """
    Flask application fixture for testing.
    """
    app = create_app('testing')  # Use the testing configuration
    with app.app_context():
        yield app

@pytest.fixture(scope='module')
def test_db(app):
    """
    Database fixture for setting up and tearing down the test database.
    """
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture(scope='function')
def db_session(test_db):
    """
    Database session fixture to provide a fresh transactional scope for each test.
    """
    connection = test_db.engine.connect()
    transaction = connection.begin()
    session = test_db.session

    logging.info("Starting new database session for test")

    yield session

    logging.info("Rolling back transaction after test")
    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture(scope='function')
def user(db_session):
    # Check if a user with the same credentials already exists
    existing_user = db_session.query(User).filter_by(email='test@example.com').first()
    if existing_user:
        db_session.delete(existing_user)
        db_session.commit()

    # Create a test user with admin privileges
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword',
        'is_admin': True  # Set is_admin to True
    }
    user = create_user(user_data)
    db_session.commit()
    yield user

@pytest.fixture(scope='function')
def logged_in_client(client, user, app):
    # Log in the test user by making a POST request to the login endpoint
    client.post('/login', data={
        'username': user.username,
        'password': 'testpassword'
    })
    return client
