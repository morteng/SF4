import pytest
from app import create_app, db

@pytest.fixture(scope="module")
def app():
    """Application fixture with database setup"""
    app = create_app(config_name='testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    """Test client fixture"""
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture(scope="function")
def db_session(app):
    """Database session fixture"""
    with app.app_context():
        yield db.session
