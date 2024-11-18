import pytest
from app import create_app
from app.extensions import db

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    return app

@pytest.fixture(scope='session')
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='session')
def db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection)
    session = db.create_scoped_session(options=options)
    yield session
    transaction.rollback()
    connection.close()
    session.remove()
