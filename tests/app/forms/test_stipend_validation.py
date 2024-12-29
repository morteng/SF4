import pytest
from datetime import datetime, timedelta
from flask_wtf.csrf import generate_csrf
from app.constants import FlashMessages
from app.forms.admin_forms import StipendForm
from app.models.organization import Organization
from app.models.tag import Tag
from app.extensions import db
from freezegun import freeze_time

@freeze_time("2024-01-01 00:00:00")
def test_valid_date_format(app, form_data):
    """Test valid date format"""
    valid_dates = [
        '2025-12-31 23:59:59',  # Standard valid date
        '2024-02-29 12:00:00',  # Leap year date
        '2025-01-01 00:00:00',  # Start of year
        '2025-12-31 00:00:00',  # End of year
        '2025-06-15 12:30:45'   # Mid-year with specific time
    ]
    
    with app.test_request_context():
        form = StipendForm()
        csrf_token = form.csrf_token.current_token
        form_data['csrf_token'] = csrf_token

        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        for date in valid_dates:
            form_data['application_deadline'] = date
            form = StipendForm(data=form_data, meta={'csrf': False})
            form.tags.choices = tag_choices
            assert form.validate() is True, f"Failed validation for date: {date}"

def test_invalid_date_format(app, form_data):
    """Test invalid date formats"""
    invalid_dates = [
        '2025-12-31',  # Missing time
        '2025-12-31 25:00:00',  # Invalid hour
        '2025-02-30 12:00:00',  # Invalid date
        'invalid-date',  # Completely invalid
    ]

    with app.test_request_context():
        form = StipendForm()
        csrf_token = form.csrf_token.current_token
        form_data['csrf_token'] = csrf_token

        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]

        for date in invalid_dates:
            form_data['application_deadline'] = date
            form = StipendForm(data=form_data, meta={'csrf': False})
            form.tags.choices = tag_choices
            assert form.validate() is False, f"Expected validation failure for date: {date}"
            assert 'application_deadline' in form.errors, f"Expected application_deadline error for date: {date}"

def test_timezone_aware_datetime(app, form_data):
    """Test timezone handling"""
    with app.test_request_context():
        form_data['application_deadline'] = '2025-12-31T23:59:59Z'  # UTC time
        form = StipendForm(data=form_data)
        assert form.validate() is True
        assert form.application_deadline.data.tzinfo is not None  # Ensure timezone is set

def test_csrf_token_validation(app, form_data):
    """Test CSRF token validation"""
    with app.test_request_context():
        del form_data['csrf_token']  # Remove CSRF token
        form = StipendForm(data=form_data)
        assert form.validate() is False
        assert 'csrf_token' in form.errors

def test_invalid_tag_id(app, form_data):
    """Test invalid tag ID"""
    with app.test_request_context():
        form_data['tags'] = [99999]  # Invalid tag ID
        form = StipendForm(data=form_data)
        assert form.validate() is False
        assert 'tags' in form.errors

def test_invalid_organization_id(app, form_data):
    """Test invalid organization ID"""
    with app.test_request_context():
        form_data['organization_id'] = 99999  # Invalid org ID
        form = StipendForm(data=form_data)
        assert form.validate() is False
        assert 'organization_id' in form.errors
