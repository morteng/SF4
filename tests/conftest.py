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

    @pytest.fixture
    def stipend_data(db_session):
        """Fixture providing base stipend data"""
        org = Organization(name="Test Org", description="Test Description")
        db_session.add(org)
        db_session.commit()
    
        return {
            'name': 'Test Stipend',
            'summary': 'Test summary',
            'description': 'Test description',
            'homepage_url': 'http://example.com',
            'application_procedure': 'Test procedure',
            'eligibility_criteria': 'Test criteria',
            'application_deadline': '2024-12-31 23:59:59',
            'organization_id': org.id,
            'open_for_applications': True
        }

    @pytest.fixture
    def logged_in_admin(client, db_session):
        """Fixture to log in as admin user"""
        from app.models.user import User
        from werkzeug.security import generate_password_hash
    
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('testpass'),
            is_admin=True
        )
        db_session.add(admin)
        db_session.commit()
    
        # Log in as admin
        client.post('/login', data={
            'username': 'admin',
            'password': 'testpass'
        })
        return client
