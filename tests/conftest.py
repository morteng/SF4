import pytest
from flask import Flask
from app import create_app  # Adjust this based on your application structure
from app.extensions import db  # Import the existing SQLAlchemy instance
from flask_login import login_user
from app.models.user import User  # Import the User model

# Define the app fixture
@pytest.fixture(scope='module')
def app():
    app = create_app('testing')  # or whichever config you use for testing
    return app

# Define the _db fixture
@pytest.fixture(scope='module')
def _db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

# Optionally, define a db fixture that provides the session
@pytest.fixture(scope='function')
def db(_db):
    connection = _db.engine.connect()
    transaction = connection.begin()
    session = _db.session

    yield session  # provide the session to tests

    transaction.rollback()
    connection.close()
    session.remove()

# Define the logged_in_client fixture
@pytest.fixture(scope='function')
def logged_in_client(app, db):
    client = app.test_client()
    with app.app_context():
        # Create a user and log them in
        user = User(username='testuser', password='testpassword')
        db.session.add(user)
        db.session.commit()
        login_user(user)
        yield client
        # Clean up after the test
        db.session.delete(user)
        db.session.commit()
