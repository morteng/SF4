import pytest
from app.utils import init_admin_user
from app.models.user import User
from app.extensions import db

@pytest.fixture(scope='function')
def admin_user(session):
    # Create an admin user for testing
    admin = User(
        username='admin_user',
        email='admin@example.com',
        is_admin=True
    )
    admin.set_password('admin_password')
    session.add(admin)
    session.commit()
    yield admin

def test_init_admin_user_existing(app, session):
    with app.app_context():
        init_admin_user()
        # Check if the admin user still exists and has not been recreated
        admin = User.query.filter_by(username='admin_user').first()
        assert admin is not None
        assert admin.is_admin is True

def test_init_admin_user_new(app, session):
    with app.app_context():
        # Delete existing admin user to simulate a new setup
        User.query.filter_by(username='admin_user').delete()
        session.commit()

        init_admin_user()
        # Check if the admin user has been created correctly
        admin = User.query.filter_by(username='admin_user').first()
        assert admin is not None
        assert admin.is_admin is True
        assert admin.check_password('admin_password') is True
