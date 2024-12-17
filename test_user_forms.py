import pytest
from app.forms.user_forms import ProfileForm, LoginForm
from app.models.user import User
from werkzeug.security import generate_password_hash

def test_profile_form_valid(client, db_session):
    form = ProfileForm(original_username="testuser", original_email="test@example.com")
    form.username.data = "newusername"
    form.email.data = "newemail@example.com"
    assert form.validate() == True

def test_profile_form_invalid_same_username(client, db_session):
    password_hash = generate_password_hash("password123")
    user = User(username="existinguser", email="existing@example.com", password_hash=password_hash)
    db_session.add(user)
    db_session.commit()

    form = ProfileForm(original_username="testuser", original_email="test@example.com")
    form.username.data = "existinguser"
    form.email.data = "newemail@example.com"
    assert form.validate() == False
    assert 'Please use a different username.' in form.username.errors

def test_profile_form_invalid_same_email(client, db_session):
    password_hash = generate_password_hash("password123")
    user = User(username="existinguser", email="existing@example.com", password_hash=password_hash)
    db_session.add(user)
    db_session.commit()

    form = ProfileForm(original_username="testuser", original_email="test@example.com")
    form.username.data = "newusername"
    form.email.data = "existing@example.com"
    assert form.validate() == False
    assert 'Please use a different email address.' in form.email.errors

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
