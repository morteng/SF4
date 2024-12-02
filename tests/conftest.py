import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import create_app  # Adjust this based on your application structure

# Define the app fixture
@pytest.fixture(scope='module')
def app():
    app = create_app('testing')  # or whichever config you use for testing
    return app

# Define the _db fixture
@pytest.fixture(scope='module')
def _db(app):
    db = SQLAlchemy(app)
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
