import pytest
from app import create_app
from app.forms.admin_forms import OrganizationForm
from app.config import TestConfig

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app('testing')
    return app

def test_organization_form_valid_data(app):
    """Test organization form with valid data"""
    with app.test_request_context():
        # Initialize session and CSRF token
        client = app.test_client()
        client.get('/')  # Access any route to initialize session
        
        with client.session_transaction() as session:
            form = OrganizationForm(
                data={
                    'name': 'Valid Org',
                    'description': 'Valid description',
                    'homepage_url': 'https://valid.org'
                },
                meta={'csrf': False}  # Disable CSRF for testing
            )
            assert form.validate() is True
            assert form.errors == {}

def test_organization_form_required_fields(app):
    """Test organization form with missing required fields"""
    with app.test_request_context():
        # Initialize session and CSRF token
        client = app.test_client()
        client.get('/')  # Access any route to initialize session
        
        with client.session_transaction() as session:
            form = OrganizationForm(
                data={},
                meta={'csrf': False}  # Disable CSRF for testing
            )
            assert not form.validate()
            assert 'name' in form.errors
            assert 'homepage_url' in form.errors
            assert 'This field is required.' in form.name.errors

def test_organization_form_name_validation(app):
    """Test organization name validation rules"""
    with app.test_request_context():
        # Initialize session and CSRF token
        client = app.test_client()
        client.get('/')  # Access any route to initialize session
        
        with client.session_transaction() as session:
            # Test invalid characters
            form = OrganizationForm(
                data={
                    'name': 'Invalid@Org!',
                    'description': 'Valid description',
                    'homepage_url': 'https://valid.org'
                },
                meta={'csrf': False}  # Disable CSRF for testing
            )
            assert not form.validate()
            assert 'name' in form.errors
            assert 'Organization name must contain only letters, numbers, and spaces.' in form.name.errors

            # Test max length
            long_name = 'a' * 101
            form = OrganizationForm(
                data={
                    'name': long_name,
                    'description': 'Valid description',
                    'homepage_url': 'https://valid.org'
                },
                meta={'csrf': False}  # Disable CSRF for testing
            )
            assert not form.validate()
            assert 'name' in form.errors
            assert 'Organization name cannot exceed 100 characters.' in form.name.errors

def test_organization_form_url_validation(app):
    """Test homepage URL validation"""
    with app.test_request_context():
        # Initialize session and CSRF token
        client = app.test_client()
        client.get('/')  # Access any route to initialize session
        
        with client.session_transaction() as session:
            # Test invalid URL format
            form = OrganizationForm(
                data={
                    'name': 'Valid Org',
                    'description': 'Valid description',
                    'homepage_url': 'not-a-url'
                },
                meta={'csrf': False}  # Disable CSRF for testing
            )
            assert form.validate() is False
            assert 'Please enter a valid URL starting with http:// or https://.' in form.homepage_url.errors
            assert 'URL must start with http:// or https://.' in form.homepage_url.errors

            # Test valid URL
            form = OrganizationForm(
                data={
                    'name': 'Valid Org',
                    'description': 'Valid description',
                    'homepage_url': 'https://valid.org'
                },
                meta={'csrf': False}  # Disable CSRF for testing
            )
            assert form.validate() is True

def test_organization_form_description_validation(app, client):
    """Test description field validation"""
    with app.test_request_context():
        # Initialize session and CSRF token
        client.get('/')
        
        # Test max length
        long_desc = 'a' * 501
        form = OrganizationForm(data={
            'name': 'Valid Org',
            'description': long_desc,
            'homepage_url': 'https://valid.org'
        }, meta={'csrf': False})
        assert not form.validate()
        assert 'Description cannot exceed 500 characters.' in form.description.errors

        # Test optional field
        form = OrganizationForm(data={
            'name': 'Valid Org',
            'description': '',
            'homepage_url': 'https://valid.org'
        }, meta={'csrf': False})
        assert form.validate() is True
