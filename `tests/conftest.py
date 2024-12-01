import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture
def db(app):
    return _db

@pytest.fixture
def logged_in_client(app, client):
    # Create a test user and log them in
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword')
        _db.session.add(user)
        _db.session.commit()
        user_id = user.id  # store the id immediately
    
    # Log the user in
    with client.session_transaction() as sess:
        sess['user_id'] = user_id

    yield client
