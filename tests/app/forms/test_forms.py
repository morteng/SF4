import pytest
from app import create_app
from app.forms.admin_forms import OrganizationForm
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_organization_form_valid_data(app, client):
    """Test organization form with valid data"""
    with app.app_context():
        # Create form to generate CSRF token
        form = OrganizationForm()
        
        # Get CSRF token from form
        csrf_token = form.csrf_token.current_token
        
        # Test form validation with CSRF token
        form = OrganizationForm(data={
            'name': 'Valid Org',
            'description': 'Valid description',
            'homepage_url': 'https://valid.org',
            'csrf_token': csrf_token
        })
        
        # Debug logging for validation errors
        if not form.validate():
            print("Form validation errors:", form.errors)
            
        assert form.validate()
