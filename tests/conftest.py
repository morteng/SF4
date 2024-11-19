import pytest
from app import create_app, db

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
    # Use db.session instead of _db.create_scoped_session
    session = _db.sessionmaker(bind=_db.engine, **options)()
    yield session
    session.rollback()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        yield client
