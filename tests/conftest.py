import os
import sys
import pytest
from app import create_app  
from app.extensions import db  
from sqlalchemy.orm import scoped_session, sessionmaker

tests_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.dirname(tests_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

@pytest.fixture(scope='session', autouse=True)
def setup_directories():
    instance_dir = '/home/morten/sf4/instance'
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)

@pytest.fixture(scope='session')
def app(setup_directories):
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/morten/sf4/instance/site.db'
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
    from app.models.user import User 
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
    return response.headers.get('Authorization')  