import pytest
from app import create_app
from app.extensions import db

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    return app

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def session(app):
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def init_database(app, session):
    with app.app_context():
        # Create admin user or other initial data if needed
        from app.utils import init_admin_user
        init_admin_user()
    return None
