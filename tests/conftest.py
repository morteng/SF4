import pytest
from sqlalchemy.orm import scoped_session, sessionmaker
from app import create_app, db as _db
from app.models.user import User
from app.models.bot import Bot  # Import the Bot model
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='session')
def app():
    from app import create_app
    app = create_app('testing')
    return app

@pytest.fixture(scope='session')
def db(app):
    """Set up the database for testing"""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture(scope='module')
def session(db):
    """Create a new database session for a test module"""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Create a session factory
    session_factory = sessionmaker(bind=connection)
    # Create a scoped session
    session = scoped_session(session_factory)
    
    yield session
    
    # Rollback the transaction and close the connection
    session.remove()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope='module', autouse=True)
def init_admin_user(session):
    # First try to find existing admin user
    admin_user = session.query(User).filter_by(email='admin@example.com').first()
    if not admin_user:
        admin_user = User(
            username='admin_user',
            password_hash=generate_password_hash('secure_password'),
            email='admin@example.com',
            is_admin=True
        )
        session.add(admin_user)
        session.commit()
        # Generate token for the admin user
        admin_user.generate_auth_token()

@pytest.fixture
def admin_token(session):
    """Get admin authentication token"""
    admin_user = session.query(User).filter_by(email='admin@example.com').first()
    if not admin_user.auth_token:
        admin_user.generate_auth_token()
    return admin_user.auth_token

@pytest.fixture
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

@pytest.fixture(scope='module')
def client(app):
    """Create a test client"""
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client
