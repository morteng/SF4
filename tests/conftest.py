import pytest
from app import create_app, db, run_migrations  # Import the run_migrations function
from app.models.user import User
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='module')
def init_database(test_client):
    # Initialize the database and apply migrations
    with test_client.application.app_context():
        db.create_all()
        run_migrations()  # Apply migrations
        yield
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def admin_user(init_database, test_client):
    # Create an admin user if it doesn't exist
    from app.extensions import db
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
        return admin

@pytest.fixture(scope='module')
def admin_token(test_client, admin_user):
    # Log in the admin user and get the token
    response = test_client.post('/admin/login', data={
        'username': admin_user.username,
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Assuming the login returns a session cookie for authentication
    return response.cookies['session']
