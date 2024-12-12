import pytest
from app import create_app
from app.forms.admin_forms import UserForm
from app.models.user import User
from app.extensions import db

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
        # Ensure a user exists in the database for validation logic
        user = User(username='test_user', email='test@example.com')
        db.session.add(user)
        db.session.commit()

        form = UserForm(original_username='test_user', original_email='test@example.com', data={
            'username': 'test_user',
            'email': 'test@example.com'
        })
        assert form.validate() == True  # Assuming you want to check if the form validates correctly
