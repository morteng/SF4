import pytest
from app import create_app
from app.extensions import db

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def test_db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture(scope='function')
def session(test_db, app):
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection)
    session = db.create_scoped_session(options=options)
    db.session = session

    yield session

    session.close()
    transaction.rollback()
    connection.close()
