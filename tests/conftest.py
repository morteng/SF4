import pytest
from app import create_app
from app.extensions import db as _db

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    # Use the testing configuration
    app = create_app('testing')

    # Create an application context before running tests
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    """Create a new database for the test session."""
    _db.create_all()

    yield _db

    # Drop all tables after tests are done
    _db.drop_all()

@pytest.fixture(scope='function')
def session(db, request):
    """Create a new database session for each test function."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection)
    session = db.create_scoped_session(options=options)

    yield session

    # Rollback the transaction and close the session after each test
    session.rollback()
    connection.close()
    session.remove()
