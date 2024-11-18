import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture(scope='module')
def admin_user(test_client):
    with test_client.application.app_context():
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('securepassword')
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture(scope='module')
def admin_token(test_client, admin_user):
    with test_client:
        response = test_client.post(url_for('public_user.login'), data={
            'username': admin_user.username,
            'password': 'securepassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        return test_client.cookie_jar
