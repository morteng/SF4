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
        db.create_all()  # Ensure all tables are created

        user = User(username='test_user', email='test@example.com')
        user.set_password('secure_password')  # Ensure the password is hashed
        db.session.add(user)
        db.session.commit()

        form = UserForm(
            original_username='test_user',
            original_email='test@example.com',
            data={
                'username': 'test_user',
                'email': 'test@example.com',
                'password': 'secure_password',  # Password is required
                'is_admin': False  # Optional field
            }
        )
        assert form.validate() == True
