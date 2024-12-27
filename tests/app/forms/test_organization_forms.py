import pytest
from app import create_app
from app.forms.admin_forms import OrganizationForm
from app.config import TestConfig

@pytest.fixture
def app():
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
            assert 'description' in form.errors
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
            assert 'Invalid URL format.' in form.homepage_url.errors

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

def test_organization_form_description_validation(app):
    """Test description field validation"""
    with app.app_context():
        # Test max length
        long_desc = 'a' * 501
        form = OrganizationForm(data={
            'name': 'Valid Org',
            'description': long_desc,
            'homepage_url': 'https://valid.org'
        })
        assert form.validate() is False
        assert 'Field must be between 0 and 500 characters long.' in form.description.errors

        # Test optional field
        form = OrganizationForm(data={
            'name': 'Valid Org',
            'description': '',
            'homepage_url': 'https://valid.org'
        })
        assert form.validate() is True
