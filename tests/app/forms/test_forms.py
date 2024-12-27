import pytest
from app import create_app
from app.forms.admin_forms import OrganizationForm
from app.config import TestConfig

@pytest.fixture
def app():
    app = create_app('testing')  # Use 'testing' instead of TestConfig
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_organization_form_valid_data(app):
    """Test organization form with valid data"""
    # Create form with valid data, disabling CSRF for testing
    form = OrganizationForm(
        data={
            'name': 'Valid Org',
            'description': 'Valid description',
            'homepage_url': 'https://valid.org'
        },
        meta={'csrf': False}
    )
    
    # Validate the form and print errors if validation fails
    assert form.validate(), f"Form validation failed with errors: {form.errors}"

@pytest.mark.parametrize("name,description,homepage_url,expected", [
    ("", "Valid description", "https://valid.org", False),  # Missing name
    ("Valid Org", "", "https://valid.org", False),  # Missing description
    ("Valid Org", "Valid description", "invalid-url", False),  # Invalid URL
    ("Valid Org", "Valid description", "", False),  # Missing URL
    ("a" * 256, "Valid description", "https://valid.org", False),  # Name too long
])
def test_organization_form_invalid_data(app, client, name, description, homepage_url, expected):
    """Test organization form with invalid data"""
    with app.app_context():
        with client.session_transaction() as session:
            form = OrganizationForm()
            csrf_token = form.csrf_token.current_token
            
            form = OrganizationForm(data={
                'name': name,
                'description': description,
                'homepage_url': homepage_url,
                'csrf_token': csrf_token
            })
            
            if not form.validate():
                print(f"Validation errors for {name}, {description}, {homepage_url}:", form.errors)
                
            assert form.validate() == expected
