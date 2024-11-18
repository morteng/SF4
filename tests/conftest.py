import pytest
from sqlalchemy.orm import scoped_session, sessionmaker
from app import create_app, db as _db
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
        # Import all models to ensure they're registered with SQLAlchemy
        from app.models import User, Bot, Stipend, Tag, Organization, Notification
        
        # Create all tables
        _db.create_all()
        
        yield _db
        
        # Drop all tables after tests
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
    """Initialize admin user with auth token"""
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
    
    # Always generate a fresh token
    admin_user.generate_auth_token()
    session.commit()
    return admin_user

@pytest.fixture
def admin_token(init_admin_user):
    """Get admin authentication token"""
    return init_admin_user.auth_token

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
