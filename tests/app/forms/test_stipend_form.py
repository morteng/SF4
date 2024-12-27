import pytest
from datetime import datetime, timedelta
from app.forms.admin_forms import StipendForm
from app.models.organization import Organization
from app.extensions import db
from app.forms.fields import CustomDateTimeField
from wtforms import Form, StringField

@pytest.fixture
def form_data():
    return {
        'name': 'Test Stipend',
        'summary': 'Test summary',
        'description': 'Test description',
        'homepage_url': 'https://example.com',
        'application_procedure': 'Test procedure',
        'eligibility_criteria': 'Test criteria',
        'organization_id': 1,
        'open_for_applications': True
    }

def test_valid_date_format(app, form_data):
    """Test valid date format"""
    form_data['application_deadline'] = '2025-12-31 23:59:59'
    with app.test_request_context():
        # Create a test organization
        org = Organization(name="Test Org", description="Test Description", homepage_url="https://test.org")
        db.session.add(org)
        db.session.commit()
        form_data['organization_id'] = org.id

        # Get CSRF token
        form = StipendForm()
        csrf_token = form.csrf_token.current_token
        form_data['csrf_token'] = csrf_token

        # Validate the form
        form = StipendForm(data=form_data, meta={'csrf': False})
        if not form.validate():
            print("Validation errors:", form.errors)
        assert form.validate() is True

def test_invalid_date_format(app, form_data):
    """Test invalid date formats"""
    invalid_dates = [
        '2025-12-31',  # Missing time
        '2025/12/31 23:59:59',  # Wrong date separator
        '31-12-2025 23:59:59',  # Wrong date order
        '2025-12-31 25:61:61',  # Invalid time
        '2025-02-30 12:00:00',  # Invalid date (Feb 30)
    ]
    
    with app.test_request_context():
        for date in invalid_dates:
            form_data['application_deadline'] = date
            form = StipendForm(data=form_data)
            assert form.validate() is False
            assert 'application_deadline' in form.errors

def test_past_date(app, form_data):
    """Test past date validation"""
    yesterday = datetime.now() - timedelta(days=1)
    form_data['application_deadline'] = yesterday.strftime('%Y-%m-%d %H:%M:%S')
    with app.test_request_context():
        form = StipendForm(data=form_data)
        assert form.validate() is False
        assert 'Application deadline must be a future date' in form.errors['application_deadline']

def test_future_date_limit(app, form_data):
    """Test future date limit (5 years)"""
    future_date = datetime.now().replace(year=datetime.now().year + 6)
    form_data['application_deadline'] = future_date.strftime('%Y-%m-%d %H:%M:%S')
    with app.test_request_context():
        form = StipendForm(data=form_data)
        assert form.validate() is False
        assert 'Application deadline cannot be more than 5 years in the future' in form.errors['application_deadline']

def test_time_component_validation(app, form_data):
    """Test time component validation"""
    invalid_times = [
        '2025-12-31 24:00:00',  # Invalid hour
        '2025-12-31 23:60:00',  # Invalid minute
        '2025-12-31 23:59:60',  # Invalid second
    ]
    
    with app.test_request_context():
        for time in invalid_times:
            form_data['application_deadline'] = time
            form = StipendForm(data=form_data)
            assert form.validate() is False
            assert 'application_deadline' in form.errors

# def test_leap_year_validation(app, form_data):
#     """Test leap year validation"""
#     with app.test_request_context():
#         # Create a test organization
#         org = Organization(name="Test Org", description="Test Description", homepage_url="https://test.org")
#         db.session.add(org)
#         db.session.commit()
#         form_data['organization_id'] = org.id

#         # Get CSRF token
#         form = StipendForm()
#         csrf_token = form.csrf_token.current_token
#         form_data['csrf_token'] = csrf_token

#         # Valid leap year date within 5-year limit
#         form_data['application_deadline'] = '2028-02-29 12:00:00'  # 2028 is a leap year
#         form = StipendForm(data=form_data, meta={'csrf': False})
#         if not form.validate():
#             print("Validation errors:", form.errors)
#         assert form.validate() is True
        
#         # Invalid leap year date
#         form_data['application_deadline'] = '2023-02-29 12:00:00'
#         form = StipendForm(data=form_data, meta={'csrf': False})
#         assert form.validate() is False
#         if not form.validate():
#             print("Validation errors:", form.errors)
#         assert any('Invalid date values (e.g., Feb 29 in non-leap years)' in error for error in form.errors['application_deadline'])

def test_missing_date(app, form_data):
    """Test missing date validation"""
    with app.test_request_context():
        # Add the key with a dummy value before deleting it
        form_data['application_deadline'] = '2025-12-31 23:59:59'
        del form_data['application_deadline']
        form = StipendForm(data=form_data, meta={'csrf': False})
        assert form.validate() is False
        assert 'Date is required.' in form.errors['application_deadline']

class TestForm(Form):
    test_field = CustomDateTimeField(
        label='Test Field',
        format='%Y-%m-%d %H:%M:%S',
        timezone='UTC',
        error_messages={
            'required': 'Date is required',
            'invalid_format': 'Invalid date format',
            'invalid_date': 'Invalid date values (e.g., Feb 30, Feb 31)',
            'invalid_time': 'Invalid time values (e.g., 25:00:00, 12:60:00)',
            'invalid_timezone': 'Invalid timezone',
            'past_date': 'Date must be a future date',
            'future_date': 'Date cannot be more than 5 years in the future',
            'invalid_leap_year': 'Invalid date values (e.g., Feb 29 in non-leap years)'
        }
    )

def test_leap_year_validation_simplified(app):
    """Test leap year validation directly on CustomDateTimeField."""
    with app.test_request_context():
        field = TestForm().test_field

        # Test with a valid leap year date
        field.process_formdata(['2028-02-29 12:00:00'])
        assert field.validate(TestForm()) is True
        assert field.errors == []

        # Reset errors for next test
        field.errors = []

        # Test with an invalid leap year date
        field.process_formdata(['2023-02-29 12:00:00'])
        assert field.validate(TestForm()) is False
        assert 'Invalid date values (e.g., Feb 29 in non-leap years)' in field.errors
