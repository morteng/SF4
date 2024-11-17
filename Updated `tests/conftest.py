import pytest
from app import create_app, db
from app.models.user import User
from app.models.bot import Bot

@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test session."""
    # Create the app with common test config
    app = create_app('testing')

    # Create an application context before running tests
    with app.app_context():
        yield app

@pytest.fixture(scope='module')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='module', autouse=True)
def init_database(app, session):
    """Create and initialize the database before each test session."""
    # Create all tables
    db.create_all()
    yield
    # Drop all tables after tests are done
    db.drop_all()

@pytest.fixture(scope='function')
def session(app, db):
    """A new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection)
    session = db.create_scoped_session(options=options)
    yield session
    session.remove()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope='module')
def admin_user(app, session):
    """Create test admin user"""
    user = User(
        username='admin_test',
        email='admin@test.com',
        is_admin=True
    )
    user.set_password('test_password')
    session.add(user)
    session.commit()
    return user

@pytest.fixture(scope='module')
def admin_token(admin_user):
    """Generate admin authentication token"""
    return admin_user.generate_auth_token()

@pytest.fixture(scope='module')
def test_bot(session):
    """Create test bot"""
    bot = Bot(
        name='Test Bot',
        description='Test Description',
        status='active'
    )
    session.add(bot)
    session.commit()
    return bot
