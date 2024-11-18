import pytest
from app import create_app, db, run_migrations  # Import the run_migrations function
from app.models.user import User
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        run_migrations()  # Run migrations before tests
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def admin_user(test_client):
    # Create an admin user if it doesn't exist
    with test_client.application.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=generate_password_hash('password'),
                email='admin@example.com',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
        yield admin

@pytest.fixture(scope='function')
def admin_token(test_client, admin_user):
    # Log in the admin user and get the token
    with test_client.application.app_context():
        response = test_client.post('/admin/login', data={
            'username': admin_user.username,
            'password': 'password'
        }, follow_redirects=True)
        assert response.status_code == 200
        # Assuming the login returns a session cookie for authentication
        yield response.headers.get('Set-Cookie')
