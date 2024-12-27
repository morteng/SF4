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

def test_organization_form_valid_data(app, client):
    """Test organization form with valid data"""
    # Initialize session with CSRF token
    with client.session_transaction() as session:
        session['csrf_token'] = 'test_csrf_token'
    
    # Make a request to initialize the session
    client.get('/')
    
    with app.test_request_context():
        # Create form within the request context
        form = OrganizationForm()
        
        # Verify CSRF token in session
        with client.session_transaction() as session:
            print("Session contents:", session)  # Debug session state
            assert 'csrf_token' in session, "CSRF token not found in session"
            assert form.csrf_token.current_token == session['csrf_token'], "CSRF token mismatch"
            
            # Test form validation with CSRF token
            # Get CSRF token from the form
            csrf_token = form.csrf_token.current_token
            
            form = OrganizationForm(data={
                'name': 'Valid Org',
                'description': 'Valid description',
                'homepage_url': 'https://valid.org',
                'csrf_token': csrf_token
            })
            
            # Debug logging for validation errors and response
            if not form.validate():
                print("Form validation errors:", form.errors)
                print("Response status:", form.validate())
                
            assert form.validate()

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
