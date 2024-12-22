import pytest
from app.models.user import User
from app.services.user_service import create_user, delete_user, get_user_by_id, get_all_users
from app.forms.admin_forms import UserForm  # Import the UserForm class
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

def test_create_user(db_session, user_data):
    user = create_user(user_data)
    assert user.username == user_data['username']
    assert user.email == user_data['email']

    db_session.expire_all()
    saved_user = db_session.query(User).filter_by(email=user_data['email']).first()
    assert saved_user is not None
    assert saved_user.username == user_data['username']
    assert saved_user.email == user_data['email']


def test_create_user_duplicate_email(db_session, admin_user, user_data, app):
    with app.app_context():
        # Re-query the admin_user to ensure it is attached to the session
        admin_user = db_session.query(User).filter_by(id=admin_user.id).one()

        # Create a user first to cause a duplicate email error
        existing_user = User(
            username='existing_user',
            email=user_data['email'],
            password_hash=generate_password_hash(user_data['password']),
            is_admin=False
        )
        db_session.add(existing_user)
        db_session.commit()

        # Attempt to create another user with the same email
        duplicate_user_data = {
            'username': 'duplicate_user',
            'email': user_data['email'],
            'password': 'password123'
        }

        with pytest.raises(IntegrityError):
            new_user = User(
                username=duplicate_user_data['username'],
                email=duplicate_user_data['email'],
                password_hash=generate_password_hash(duplicate_user_data['password']),
                is_admin=False
            )
            db_session.add(new_user)
            db_session.commit()


def test_get_user_by_id(db_session, admin_user):
    user = get_user_by_id(admin_user.id)
    assert user is not None
    assert user.username == admin_user.username
    assert user.email == admin_user.email


def test_get_all_users(db_session, admin_user):
    users = get_all_users()
    assert len(users) >= 1
    assert admin_user in users


def test_delete_user(db_session, admin_user):
    delete_user(admin_user)
    db_session.expire_all()
    user = db_session.get(User, admin_user.id)
    assert user is None

def test_user_form_validate(app):
    with app.app_context():
        form = UserForm(
            original_username='test_user',
            original_email='test@example.com',
            data={
                'username': 'test_user',  # Matches the original
                'email': 'test@example.com',  # Matches the original
                'password': 'secure_password',  # Required field
                'is_admin': False
            }
        )
        # Add more assertions as needed to validate the form
        assert form.validate() == True  # Example assertion, adjust as necessary
