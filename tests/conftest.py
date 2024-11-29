import sys
from pathlib import Path
import pytest
from app.models.user import User
from app.extensions import db
from flask_login import login_user

# Get the project root directory
root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

from app import create_app

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    return app

@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def admin_user(app):
    with app.app_context():
        user = User(username='admin', email='admin@example.com', is_admin=True)
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        yield user
        # Cleanup if needed
        db.session.delete(user)
        db.session.commit()

@pytest.fixture(scope='function')
def logged_in_client(app, admin_user):
    with app.test_client() as client:
        with app.app_context():
            login_user(admin_user)
        yield client
