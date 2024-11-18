import pytest
from app import create_app, db as _db
from app.models.user import User
from app.models.bot import Bot
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

@pytest.fixture(scope='function')
def session(db):
    """Create a new database session for a test"""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Create a session bound to the connection
    session = db.create_scoped_session(options=dict(bind=connection, binds={}))
    
    yield session
    
    # Rollback the transaction and close the connection
    session.close()
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

@pytest.fixture
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

@pytest.fixture
def admin_token(admin_user):
    """Generate admin authentication token"""
    return admin_user.generate_auth_token()

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
