import pytest
from app import create_app, db

@pytest.fixture(scope='session')
def app():
    from app.config import get_config  # Corrected import
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def session(app, db):
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection)
    session = db.create_scoped_session(options=options)
    yield session
    session.remove()
    transaction.rollback()
    connection.close()
