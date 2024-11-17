import pytest
from app import create_app
from app.extensions import db

# Import all models to ensure they're registered
from app.models.user import User
from app.models.bot import Bot
from app.models.organization import Organization
from app.models.stipend import Stipend
from app.models.tag import Tag
from app.models.notification import Notification

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        # Ensure all tables are created
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def session(app):
    with app.app_context():
        yield db.session
        db.session.rollback()
        db.session.remove()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()
