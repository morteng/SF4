import pytest
from app import create_app, db as _db  # Note: renamed db to _db to avoid confusion
from app.models.user import User
from flask_login import LoginManager

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def db(app):
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()

@pytest.fixture(scope='function')
def client(app, db):
    return app.test_client()

@pytest.fixture(scope='function')
def logged_in_client(app, client, db):
    # Create a test user and log them in
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword')
        _db.session.add(user)
        _db.session.commit()
        
    with client:
        client.post(url_for('visitor.login'), data={'username': 'testuser', 'password': 'testpassword'})
        yield client
