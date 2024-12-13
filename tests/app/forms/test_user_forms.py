import pytest
from app.forms.user_forms import ProfileForm, LoginForm
from app import create_app

@pytest.fixture(scope='module')
def test_client():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')

    with app.test_client() as client:
        with app.app_context():
            yield client

def test_profile_form_validation(test_client):
    form = ProfileForm(original_username='testuser', original_email='test@example.com')
    form.username.data = 'newusername'
    form.email.data = 'newemail@example.com'
    assert form.validate() is True

def test_profile_form_invalid_username():
    form = ProfileForm(original_username='testuser', original_email='test@example.com')
    form.username.data = ''
    form.email.data = 'newemail@example.com'
    assert form.validate() is False
    assert 'This field is required.' in form.username.errors[0]

def test_login_form_validation():
    form = LoginForm()
    form.username.data = 'testuser'
    form.password.data = 'password123'
    assert form.validate() is True

def test_login_form_invalid_username():
    form = LoginForm()
    form.username.data = ''
    form.password.data = 'password123'
    assert form.validate() is False
    assert 'This field is required.' in form.username.errors[0]
