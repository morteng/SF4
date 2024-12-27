import pytest
from datetime import datetime, timedelta
from app.forms.admin_forms import StipendForm

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
        form = StipendForm(data=form_data)
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

def test_leap_year_validation(app, form_data):
    """Test leap year validation"""
    with app.test_request_context():
        # Valid leap year date
        form_data['application_deadline'] = '2024-02-29 12:00:00'
        form = StipendForm(data=form_data)
        assert form.validate() is True
        
        # Invalid leap year date
        form_data['application_deadline'] = '2023-02-29 12:00:00'
        form = StipendForm(data=form_data)
        assert form.validate() is False
        assert 'Invalid date for month' in form.errors['application_deadline']

def test_missing_date(app, form_data):
    """Test missing date validation"""
    with app.test_request_context():
        del form_data['application_deadline']
        form = StipendForm(data=form_data)
        assert form.validate() is False
        assert 'Date is required' in form.errors['application_deadline']
