import pytest
from app import create_app
from app.extensions import db

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def session(app):
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection)
    session = db.create_scoped_session(options=options)
    yield session
    session.remove()
    transaction.rollback()
    connection.close()
