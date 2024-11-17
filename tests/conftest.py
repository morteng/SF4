import pytest
from app import create_app
from app.extensions import db

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    return app

@pytest.fixture(scope='session')
def db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture(scope='function')
def session(db, app):
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        session = db.session
        
        yield session
        
        transaction.rollback()
        connection.close()
