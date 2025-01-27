import pytest
from app import create_app, db
from app.models.organization import Organization
from app.models.user import User
from app.models.stipend import Stipend
from app.models.tag import Tag
from werkzeug.security import generate_password_hash

@pytest.fixture(scope="function")
def app():
    app = create_app('testing')
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True,
        'WTF_CSRF_ENABLED': False
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture
def db_session(app):
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        session = db.create_scoped_session(options=dict(bind=connection, binds={}))
        try:
            yield session
        finally:
            transaction.rollback()
            connection.close()
            session.remove()

def extract_csrf_token(response_data):
    import re
    match = re.search(r'name="csrf_token" value="([^"]+)"', response_data.decode('utf-8'))
    return match.group(1) if match else None

def get_all_tags():
    return Tag.query.all()

@pytest.fixture
def logged_in_admin(client, db_session):
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('testpass'),
        is_admin=True
    )
    db_session.add(admin)
    db_session.commit()
    
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'testpass'
    })
    yield client

@pytest.fixture
def organization_data():
    return {
        'name': 'Test Organization',
        'description': 'Test Description',
        'homepage_url': 'http://test.org'
    }

@pytest.fixture
def stipend_data():
    return {
        'name': 'Test Stipend',
        'summary': 'Test summary',
        'description': 'Test description',
        'homepage_url': 'http://example.com',
        'application_procedure': 'Test procedure',
        'eligibility_criteria': 'Test criteria',
        'application_deadline': '2024-01-01',
        'organization_id': 1,
        'open_for_applications': True
    }

@pytest.fixture
def tag_data():
    return {
        'name': 'Test Tag',
        'category': 'Test Category'
    }

@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'password': 'testpass123',
        'email': 'test@example.com'
    }
