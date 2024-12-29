import pytest
from flask import Flask
from freezegun import freeze_time
from app.forms.admin_forms import OrganizationForm, StipendForm
from app.config import TestConfig
from app.extensions import db
from app.constants import FlashMessages

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
import pytest
from freezegun import freeze_time
from app.forms.admin_forms import StipendForm
from app.constants import FlashMessages

def test_stipend_form_validation():
    """Test validation of the StipendForm."""
    form = StipendForm()

    # Test valid date/time
    form.application_deadline.data = "2023-10-31 23:59:59"
    assert form.validate()

    # Test invalid date/time
    form.application_deadline.data = "invalid-date"
    assert not form.validate()
    assert FlashMessages.INVALID_DATE_FORMAT in form.application_deadline.errors

    # Test missing required field
    form.application_deadline.data = None
    assert not form.validate()
    assert FlashMessages.MISSING_FIELD_ERROR in form.application_deadline.errors

@pytest.mark.parametrize("date_str,expected_error", [
    ("2023-02-29", FlashMessages.INVALID_LEAP_YEAR_DATE),  # Invalid leap year
    ("2023-13-01", FlashMessages.INVALID_DATE_FORMAT), # Invalid month
    ("2023-00-01", FlashMessages.INVALID_DATE_FORMAT), # Invalid month
    ("2023-01-32", FlashMessages.INVALID_DATE_FORMAT), # Invalid day
    ("", FlashMessages.MISSING_DATE_FIELD),           # Missing date
    ("2023/01/01", FlashMessages.INVALID_DATE_FORMAT),# Wrong format
])
def test_date_validation(date_str, expected_error):
    form = StipendForm()
    form.application_deadline.data = f"{date_str} 12:00:00"
    assert not form.validate()
    assert expected_error in form.application_deadline.errors

@pytest.mark.parametrize("time_str,expected_error", [
    ("25:00:00", FlashMessages.INVALID_TIME_RANGE),  # Invalid hour
    ("12:60:00", FlashMessages.INVALID_TIME_RANGE),  # Invalid minute
    ("12:00:60", FlashMessages.INVALID_TIME_RANGE),  # Invalid second
    ("", FlashMessages.MISSING_TIME_FIELD),          # Missing time
    ("12-00-00", FlashMessages.INVALID_TIME_FORMAT), # Wrong format
])
def test_time_validation(time_str, expected_error):
    form = StipendForm()
    form.application_deadline.data = f"2023-01-01 {time_str}"
    assert not form.validate()
    assert expected_error in form.application_deadline.errors
