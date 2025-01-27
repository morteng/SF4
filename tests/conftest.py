import pytest
from app import create_app, db
from app.models.organization import Organization
from app.models.user import User
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
