import pytest
from app import create_app, db

# Add freezegun availability check to conftest.py
try:
    from freezegun import freeze_time  # noqa: F401
    FREEZEGUN_INSTALLED = True
except ImportError:
    FREEZEGUN_INSTALLED = False

@pytest.fixture(scope="function")
def app():
    """Application fixture with temporary database"""
    app = create_app(config_name='testing')
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True,
        'WTF_CSRF_ENABLED': False  # Disable CSRF for non-CSRF specific tests
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    """Test client fixture"""
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture(scope="function")
def db_session(app):
    """Database session fixture with proper isolation"""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        options = dict(bind=connection, binds={})
        session = db.create_scoped_session(options=options)
        
        db.session = session  # Replace the default session
        
        yield session
        
        transaction.rollback()
        connection.close()
        session.remove()
