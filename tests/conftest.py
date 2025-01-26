import pytest
from app import create_app, db

@pytest.fixture(scope="session")
def app():
    """Session-wide test application"""
    app = create_app(config_name='testing')
    with app.app_context():
        yield app

@pytest.fixture(scope="function")
def client(app):
    """Test client fixture with fresh database per test"""
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture(scope="function")
def db_session(client):
    """Database session fixture"""
    yield db.session
