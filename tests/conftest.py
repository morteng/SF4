import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='module')
def admin_user(test_client):
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('password')
        db.session.add(admin)
        db.session.commit()
        yield admin
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def admin_token(test_client, admin_user):
    response = test_client.post('/admin/login', data={
        'username': admin_user.username,
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    return response.headers['Set-Cookie']
