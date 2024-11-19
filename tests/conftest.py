import pytest
from app import create_app, db
from sqlalchemy.orm import scoped_session, sessionmaker

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    return app

@pytest.fixture(scope='session')
def _db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture(scope='function', autouse=True)
def session(_db):
    connection = _db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    # Use scoped_session(sessionmaker(bind=connection)) instead of _db.create_scoped_session(options)
    Session = scoped_session(sessionmaker(bind=connection))
    session = Session()
    yield session
    session.rollback()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        yield client
