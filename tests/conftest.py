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
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture
def logged_in_client(app, client):
    # Create a test user and log them in
    with app.app_context():
        with _db.session.begin() as session:
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpassword')
            session.add(user)
            session.commit()
            user_id = user.id  # store the id immediately
        
        # Log the user in
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
    
    yield client
