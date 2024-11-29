import sys
from pathlib import Path
import pytest
from app.models.user import User
from app.extensions import db as _db
from flask_login import login_user
import re

# Get the project root directory
root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

from app import create_app

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
    return app

@pytest.fixture(scope='module')
def module_db(app):
    with app.app_context():
        _db.create_all()
        yield _db  # Provide the database instance
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app, module_db):
    # Create a new database session for a clean state per test
    connection = _db.engine.connect()
    transaction = connection.begin()
    _db.session = _db.create_scoped_session(options={"bind": connection})
    yield _db
    _db.session.remove()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope='function')
def client(app, db):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='module', autouse=True)
def init_admin_user(module_db):
    # First try to find existing admin user
    from app.models.user import User  # Import the User model inside the fixture
    admin_user = module_db.session.query(User).filter_by(email='admin@example.com').first()
    if not admin_user:
        admin_user = User(
            username='admin_user',
            password_hash='pbkdf2:sha256:150000$XbL3IjWn$3d8Kq7J29e4gFyhiuQlZIl12tXcVU8S2R5Qx5hPZV0k=',
            email='admin@example.com',
            is_admin=True
        )
        module_db.session.add(admin_user)
        module_db.session.commit()
