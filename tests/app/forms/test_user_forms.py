import pytest
from app import create_app
from app.forms.admin_forms import UserForm

@pytest.fixture
def app():
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

def test_user_form_validate(app, client):
    with app.app_context():
        form = UserForm(original_username='test_user', original_email='test@example.com')
        assert form.validate() == True  # Assuming you want to check if the form validates correctly
