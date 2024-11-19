import pytest
from app import create_app, db
from sqlalchemy.orm import scoped_session, sessionmaker

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    return app

@pytest.fixture(scope='session')
def _db(app):
    with app.app_context():
        # Initialize database tables
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture(scope='function', autouse=True)
def session(_db, app):
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        options = dict(bind=connection, binds={})
        Session = scoped_session(sessionmaker(bind=connection))
        session = Session()
        yield session
        session.rollback()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='session')
def admin_user(_db, app):
    with app.app_context():
        admin = _db.session.query(User).filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('password123')
            _db.session.add(admin)
            _db.session.commit()
        return admin

@pytest.fixture(scope='function')
def admin_token(client, admin_user):
    response = client.post('/admin/login', data={
        'username': admin_user.username,
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    return response.headers.get('Authorization')  # Use .get() to avoid KeyError if the header is missing
