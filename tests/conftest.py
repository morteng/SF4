import pytest
from app import create_app
from app.extensions import db as _db
from app.models import init_models
from sqlalchemy.orm import scoped_session, sessionmaker

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    # Use the testing configuration
    app = create_app('testing')

    # Create an application context before running tests
    with app.app_context():
        init_models(app)  # Ensure models are initialized
        _db.create_all()  # Create all tables

        yield app

        # Drop all tables after tests are done
        _db.drop_all()

@pytest.fixture(scope='session')
def db(app):
    """Create a new database for the test session."""
    return _db

@pytest.fixture(scope='function')
def session(db, request):
    """Create a new database session for each test function."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection)
    Session = scoped_session(sessionmaker(bind=db.engine))
    session = Session()

    yield session

    # Rollback the transaction and close the session after each test
    session.rollback()
    connection.close()
    session.remove()
