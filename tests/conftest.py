import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def admin_user(app, session):
    user = User(username='admin', email='admin@example.com', is_admin=True)
    user.set_password('password')
    session.add(user)
    session.commit()
    return user

@pytest.fixture(scope='function')
def admin_token(client, admin_user):
    response = client.post('/admin/login', data={
        'username': admin_user.username,
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Assuming the token is returned in a JSON response
    return response.json.get('token')  # Adjust this based on your actual implementation
