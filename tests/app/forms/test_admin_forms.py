"""Tests for admin forms"""

import pytest
from flask import Flask
from app.configs.testing import TestingConfig
from app.extensions import db
from app.forms.admin import OrganizationForm  # Updated import path

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config.from_object(TestingConfig)
    
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
    """Test with actual required fields from OrganizationForm"""
    with app.app_context():
        form = OrganizationForm(
            data={
                'name': 'Valid Org',
                'homepage_url': 'https://valid.org'  # Add required URL field
            },
            meta={'csrf': False}
        )
        assert form.validate(), f"Errors: {form.errors}"

@pytest.mark.parametrize("name,homepage_url,expected", [  # Updated params
    ("", "https://valid.org", False),  # Missing name
    ("Valid", "invalid-url", False),   # Bad URL
    ("a"*101, "https://valid.org", False),  # Name too long
    ("Valid", "https://valid.org", True),   # Valid case
])
def test_organization_form_validation(app, name, homepage_url, expected):
    """Test organization form with invalid data"""
    with app.app_context():
        form = OrganizationForm(
            data={
                'name': name,
                'description': '',  # Description is optional
                'homepage_url': homepage_url
            },
            meta={'csrf': False}
        )
        
        assert form.validate() == expected, f"Expected validation to be {expected} for {name}, {homepage_url}"
