import pytest
from app import create_app
from app.forms.admin_forms import OrganizationForm
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app

def test_organization_form_valid_data(app):
    """Test organization form with valid data"""
    with app.app_context():
        form = OrganizationForm(data={
            'name': 'Valid Org',
            'description': 'Valid description',
            'homepage_url': 'https://valid.org'
        })
        assert form.validate() is True
        assert form.errors == {}

def test_organization_form_required_fields(app):
    """Test organization form with missing required fields"""
    with app.app_context():
        form = OrganizationForm(data={})
        assert form.validate() is False
        assert 'This field is required.' in form.name.errors

def test_organization_form_name_validation(app):
    """Test organization name validation rules"""
    with app.app_context():
        # Test invalid characters
        form = OrganizationForm(data={
            'name': 'Invalid@Org!',
            'description': 'Valid description',
            'homepage_url': 'https://valid.org'
        })
        assert form.validate() is False
        assert 'Name must contain only letters, numbers, and spaces.' in form.name.errors

        # Test max length
        long_name = 'a' * 101
        form = OrganizationForm(data={
            'name': long_name,
            'description': 'Valid description',
            'homepage_url': 'https://valid.org'
        })
        assert form.validate() is False
        assert 'Field must be between 1 and 100 characters long.' in form.name.errors

def test_organization_form_url_validation(app):
    """Test homepage URL validation"""
    with app.app_context():
        # Test invalid URL format
        form = OrganizationForm(data={
            'name': 'Valid Org',
            'description': 'Valid description',
            'homepage_url': 'not-a-url'
        })
        assert form.validate() is False
        assert 'Invalid URL format.' in form.homepage_url.errors

        # Test valid URL
        form = OrganizationForm(data={
            'name': 'Valid Org',
            'description': 'Valid description',
            'homepage_url': 'https://valid.org'
        })
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
