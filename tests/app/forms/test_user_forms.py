import pytest
from unittest.mock import patch
from flask import session
from werkzeug.security import generate_password_hash

from app.forms.user_forms import ProfileForm, LoginForm
from app import create_app
from app.models.user import User
from app.extensions import db
from app.constants import FlashMessages, FlashCategory

@pytest.fixture(scope='function', autouse=True)
def setup_database(_db):
    """Ensure the User table exists before running tests."""
    try:
        _db.create_all()
        yield
    finally:
        _db.session.rollback()
        _db.drop_all()

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')  # Ensures 'testing' config is loaded
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

def test_profile_form_valid(client, setup_database):
    form = ProfileForm(original_username="testuser", original_email="test@example.com")
    form.username.data = "newusername"
    form.email.data = "newemail@example.com"
    assert form.validate() == True

def test_profile_form_invalid_same_username(client, setup_database):
    password_hash = generate_password_hash("password123")
    user = User(username="existinguser", email="existing@example.com", password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    with client.application.app_context():
        with patch('app.forms.user_forms.flash_message') as mock_flash:
            form = ProfileForm(original_username="testuser", original_email="test@example.com")
            form.username.data = "existinguser"
            form.email.data = "newemail@example.com"
            is_valid = form.validate()
            mock_flash.assert_called_once_with(FlashMessages.USERNAME_ALREADY_EXISTS, FlashCategory.ERROR)
            assert not is_valid

def test_profile_form_invalid_same_email(client, setup_database):
    # Clean up any existing test users
    User.query.filter_by(email="existing@example.com").delete()
    db.session.commit()

    # Add a test user with a unique email
    password_hash = generate_password_hash("password123")
    user = User(username="existinguser", email="existing@example.com", password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    # Test with existing email
    form = ProfileForm(original_username="testuser", original_email="test@example.com")
    with client.application.app_context():
        with client.application.test_request_context():
            form.username.data = "newusername"
            form.email.data = "existing@example.com"
            assert not form.validate()
            assert FlashMessages.EMAIL_ALREADY_EXISTS in form.email.errors

    # Test with invalid email format
    form.email.data = "invalid-email"
    assert not form.validate()
    assert "Invalid email address." in form.email.errors

    # Clean up after the test
    User.query.filter_by(email="existing@example.com").delete()
    db.session.commit()

def test_login_form_valid(client):
    form = LoginForm()
    form.username.data = "testuser"
    form.password.data = "password123"
    assert form.validate() == True

def test_login_form_invalid_missing_username(client):
    form = LoginForm()
    form.password.data = "password123"
    assert form.validate() == False
    assert 'This field is required.' in form.username.errors

def test_login_form_invalid_missing_password(client):
    form = LoginForm()
    form.username.data = "testuser"
    assert form.validate() == False
    assert 'This field is required.' in form.password.errors
