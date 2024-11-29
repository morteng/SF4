import os
import sys
import pytest
from sqlalchemy.orm import scoped_session, sessionmaker

# Determine the absolute path of the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the project root to the Python path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from app.extensions import db as _db

@pytest.fixture(scope='session', autouse=True)
def setup_directories():
    instance_dir = '/home/morten/sf4/instance'
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)

@pytest.fixture(scope='session')
def app(setup_directories):
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/morten/sf4/instance/site.db'
    with app.app_context():
        _db.create_all()
    yield app
    with app.app_context():
        _db.drop_all()

@pytest.fixture(scope='function')
def session(app):
    with app.app_context():
        connection = _db.engine.connect()
        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=connection))
        yield db_session
        db_session.remove()
        connection.close()

@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def admin_user(session):
    from app.models.user import User
    admin = session.query(User).filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('password123')
        session.add(admin)
        session.commit()
    return admin

@pytest.fixture(scope='function')
def admin_token(client, admin_user, session):
    with app.app_context():
        with client.session_transaction() as sess:
            from flask_login import login_user
            login_user(admin_user)
            session.refresh(admin_user)  # Ensure the user is attached to the session
        cookie_header = '; '.join([f"{key}={value}" for key, value in client.cookie_jar._cookies['localhost.local']['/'].items()])
        return cookie_header
