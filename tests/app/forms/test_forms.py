import pytest
from flask import Flask
from app.forms.admin_forms import OrganizationForm
from app.config import TestConfig
from app.extensions import db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    
    # Set up in-memory SQLite database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Create all database tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Clean up after the test
    with app.app_context():
        db.drop_all()

def test_organization_form_valid_data(app):
    """Test organization form with valid data"""
    with app.app_context():
        # Create form with valid data, disabling CSRF for testing
        form = OrganizationForm(
            data={
                'name': 'Valid Org',
                'description': 'Valid description',
                'homepage_url': 'https://valid.org'
            },
            meta={'csrf': False}
        )
        
        assert form.validate(), f"Form validation failed with errors: {form.errors}"

@pytest.mark.parametrize("name,description,homepage_url,expected", [
    ("", "Valid description", "https://valid.org", False),  # Missing name
    ("Valid Org", "", "https://valid.org", True),  # Empty description is allowed
    ("Valid Org", "Valid description", "invalid-url", False),  # Invalid URL
    ("Valid Org", "Valid description", "", False),  # Missing URL
    ("a" * 256, "Valid description", "https://valid.org", False),  # Name too long
])
def test_organization_form_invalid_data(app, name, description, homepage_url, expected):
    """Test organization form with invalid data"""
    with app.app_context():
        form = OrganizationForm(
            data={
                'name': name,
                'description': description,
                'homepage_url': homepage_url
            },
            meta={'csrf': False}
        )
        
        assert form.validate() == expected, f"Expected validation to be {expected} for {name}, {description}, {homepage_url}"
import pytest
from flask import Flask
from app.forms.admin_forms import OrganizationForm
from app.config import TestConfig
from app.extensions import db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    
    # Set up in-memory SQLite database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Create all database tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Clean up after the test
    with app.app_context():
        db.drop_all()

def test_organization_form_valid_data(app):
    """Test organization form with valid data"""
    with app.app_context():
        # Create form with valid data, disabling CSRF for testing
        form = OrganizationForm(
            data={
                'name': 'Valid Org',
                'description': 'Valid description',
                'homepage_url': 'https://valid.org'
            },
            meta={'csrf': False}
        )
        
        assert form.validate(), f"Form validation failed with errors: {form.errors}"

@pytest.mark.parametrize("name,description,homepage_url,expected", [
    ("", "Valid description", "https://valid.org", False),  # Missing name
    ("Valid Org", "", "https://valid.org", True),  # Empty description is allowed
    ("Valid Org", "Valid description", "invalid-url", False),  # Invalid URL
    ("Valid Org", "Valid description", "", False),  # Missing URL
    ("a" * 256, "Valid description", "https://valid.org", False),  # Name too long
])
def test_organization_form_invalid_data(app, name, description, homepage_url, expected):
    """Test organization form with invalid data"""
    with app.app_context():
        form = OrganizationForm(
            data={
                'name': name,
                'description': description,
                'homepage_url': homepage_url
            },
            meta={'csrf': False}
        )
        
        assert form.validate() == expected, f"Expected validation to be {expected} for {name}, {description}, {homepage_url}"
