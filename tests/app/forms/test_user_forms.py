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

def test_user_form_validate(app):
    with app.app_context():
        from app.models.user import User
        from app.extensions import db

        # Create the database schema
        db.create_all()

        # Add a user to the database
        existing_user = User(username='test_user', email='test@example.com')
        existing_user.set_password('secure_password')
        db.session.add(existing_user)
        db.session.commit()

        # Provide form data matching the original user's data
        form = UserForm(
            original_username='test_user',
            original_email='test@example.com',
            data={
                'username': 'test_user',  # Matches the original
                'email': 'test@example.com',  # Matches the original
                'password': 'new_secure_password',  # Required field
                'is_admin': False  # Required checkbox
            }
        )

        # Assert that the form validates successfully
        assert form.validate() == True
