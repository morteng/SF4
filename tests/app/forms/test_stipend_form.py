import pytest
from datetime import datetime, timedelta
from flask_wtf.csrf import generate_csrf

# Check for freezegun and skip all tests if not installed
try:
    from freezegun import freeze_time
    FREEZEGUN_INSTALLED = True
except ImportError:
    FREEZEGUN_INSTALLED = False
    pytest.skip("freezegun is not installed. Run `pip install -r requirements.txt` to install dependencies.", allow_module_level=True)

# Skip time-dependent tests if freezegun is not installed
pytestmark = pytest.mark.skipif(
    not FREEZEGUN_INSTALLED,
    reason="freezegun is not installed. Run `pip install -r requirements.txt` to install dependencies."
)

from app.forms.admin_forms import StipendForm, CustomDateTimeField
from app.constants import FlashMessages
from app.models import Organization, Tag, Stipend, AuditLog
from app.forms.fields import CustomDateTimeField
from app.extensions import db
from wtforms import Form
from tests.base_test_case import BaseTestCase
from freezegun import freeze_time

# -----------------------------------------------------------------------------
# Pytest Configuration
# -----------------------------------------------------------------------------
def pytest_configure(config):
    """Add a marker for freezegun-dependent tests."""
    config.addinivalue_line(
        "markers",
        "freezegun: mark tests that require freezegun package"
    )

# -----------------------------------------------------------------------------
# Basic Field Validation Tests
# -----------------------------------------------------------------------------
def test_custom_date_time_field_validation():
    field = CustomDateTimeField()
    assert field.validate_format("2023-01-01 12:00:00") is True
    assert field.validate_format("invalid-date") is False


@pytest.mark.skipif(not FREEZEGUN_INSTALLED, reason="freezegun is not installed")
@freeze_time("2023-01-01 12:00:00")
def test_stipend_form_future_date_validation():
    form = StipendForm()
    form.application_deadline.data = datetime(2022, 12, 31, 23, 59, 59)
    assert form.validate() is False
    assert FlashMessages.INVALID_FUTURE_DATE in form.application_deadline.errors

# -----------------------------------------------------------------------------
# Valid Date Format Tests (Using freezegun)
# -----------------------------------------------------------------------------
@pytest.mark.skipif(not FREEZEGUN_INSTALLED, reason="freezegun is not installed")
@freeze_time("2024-01-01 00:00:00")
def test_valid_date_format(app, form_data, test_db):
    """Test valid date format."""
    valid_dates = [
        '2025-12-31 23:59:59',  # Standard valid date
        '2024-02-29 12:00:00',  # Leap year date
        '2025-01-01 00:00:00',  # Start of year
        '2025-12-31 00:00:00',  # End of year
        '2025-06-15 12:30:45'   # Mid-year with specific time
    ]
    
    with app.test_request_context():
        org = Organization(name="Test Org", description="Test Description", homepage_url="https://test.org")
        db.session.add(org)
        db.session.commit()

        form_data['organization_id'] = org.id
        form = StipendForm()
        csrf_token = form.csrf_token.current_token
        form_data['csrf_token'] = csrf_token

        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]

        for date_str in valid_dates:
            form_data['application_deadline'] = date_str
            form = StipendForm(data=form_data, meta={'csrf': False})
            form.tags.choices = tag_choices
            if not form.validate():
                print(f"Validation errors for {date_str}:", form.errors)
            assert form.validate() is True, f"Failed validation for date: {date_str}"

# -----------------------------------------------------------------------------
# Invalid Date Format Tests (Parametrized)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("invalid_date", [
    '2025-12-31',            # Missing time
    '2025-12-31 25:00:00',   # Invalid hour
    '2025-02-30 12:00:00',   # Invalid date
    'invalid-date',          # Completely invalid
])
def test_invalid_date_format(app, form_data, test_db, invalid_date):
    """Test invalid date formats using parametrization."""
    with app.test_request_context():
        org = Organization(name="Test Org", description="Test Description", homepage_url="https://test.org")
        db.session.add(org)
        db.session.commit()

        form_data['organization_id'] = org.id
        form_data['csrf_token'] = generate_csrf()
        form_data['application_deadline'] = invalid_date

        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices

        assert form.validate() is False, f"Expected validation failure for date: {invalid_date}"
        assert 'application_deadline' in form.errors, f"No 'application_deadline' error for date: {invalid_date}"

# -----------------------------------------------------------------------------
# Past Date Test
# -----------------------------------------------------------------------------
def test_past_date(app, form_data):
    """Test past date validation."""
    yesterday = datetime.now() - timedelta(days=1)
    form_data['application_deadline'] = yesterday.strftime('%Y-%m-%d %H:%M:%S')

    with app.test_request_context():
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices

        assert form.validate() is False
        assert 'Application deadline must be a future date' in form.errors['application_deadline']

# -----------------------------------------------------------------------------
# Future Date Limit (5 years)
# -----------------------------------------------------------------------------
def test_future_date_limit(app, form_data, test_db):
    """Test future date limit (5 years)."""
    from app.models import Tag, Organization

    db.session.query(Tag).delete()
    db.session.query(Organization).delete()
    db.session.commit()

    tag = Tag(name="Test Tag", category="Test Category")
    org = Organization(name="Test Org", description="Test Description", homepage_url="https://test.org")
    db.session.add(tag)
    db.session.add(org)
    db.session.commit()

    future_date = datetime.now().replace(year=datetime.now().year + 6)
    form_data['application_deadline'] = future_date.strftime('%Y-%m-%d %H:%M:%S')

    with app.test_request_context():
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices
        
        assert form.validate() is False
        assert 'Application deadline cannot be more than 5 years in the future' in form.errors['application_deadline']

# -----------------------------------------------------------------------------
# Invalid Time Components (Parametrized)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("invalid_time", [
    '2025-12-31 24:00:00',  # Invalid hour
    '2025-12-31 23:60:00',  # Invalid minute
    '2025-12-31 23:59:60',  # Invalid second
])
def test_invalid_time_components(app, form_data, invalid_time):
    """Test invalid time components using parametrization."""
    with app.test_request_context():
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        form_data['application_deadline'] = invalid_time
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices

        assert form.validate() is False, f"Form unexpectedly validated for time: {invalid_time}"
        assert 'application_deadline' in form.errors

# -----------------------------------------------------------------------------
# Empty or Missing Application Deadline
# -----------------------------------------------------------------------------
def test_empty_application_deadline(app, form_data):
    """Test validation when application_deadline is empty."""
    with app.test_request_context():
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        invalid_data = form_data.copy()
        invalid_data['application_deadline'] = ''

        form = StipendForm(data=invalid_data, meta={'csrf': False})
        form.tags.choices = tag_choices

        assert form.validate() is False
        assert 'application_deadline' in form.errors
        assert 'Application deadline is required.' in form.errors['application_deadline']


def test_missing_application_deadline(app, form_data):
    """Test validation when application_deadline is missing."""
    with app.test_request_context():
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        invalid_data = form_data.copy()
        del invalid_data['application_deadline']

        form = StipendForm(data=invalid_data, meta={'csrf': False})
        form.tags.choices = tag_choices

        assert form.validate() is False
        assert 'application_deadline' in form.errors
        assert 'Application deadline is required.' in form.errors['application_deadline']

# -----------------------------------------------------------------------------
# Missing Required Fields
# -----------------------------------------------------------------------------
def test_missing_required_fields(app, form_data):
    """Test validation of all required fields."""
    required_fields = [
        'name', 'summary', 'description', 'homepage_url',
        'application_procedure', 'eligibility_criteria',
        'application_deadline', 'organization_id'
    ]

    with app.test_request_context():
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]

        # Test empty strings
        for field in required_fields:
            if field != 'organization_id':  # handle differently for SelectField
                invalid_data = form_data.copy()
                invalid_data[field] = ''
                form = StipendForm(data=invalid_data, meta={'csrf': False})
                form.tags.choices = tag_choices

                assert form.validate() is False, f"Form should be invalid when {field} is empty"
                assert field in form.errors, f"Expected error for empty {field}"

        # Test missing fields
        for field in required_fields:
            invalid_data = form_data.copy()
            del invalid_data[field]

            form = StipendForm(data=invalid_data, meta={'csrf': False})
            form.tags.choices = tag_choices
            if field == 'organization_id':
                form.organization_id.choices = [(1, 'Test Org')]  # Dummy choice

            assert form.validate() is False, f"Form should be invalid when {field} is missing"
            assert field in form.errors, f"Expected error for missing {field}"

            # Special check for application_deadline
            if field == 'application_deadline':
                assert any(
                    msg in form.errors['application_deadline']
                    for msg in [
                        'Application deadline is required.',
                        'Invalid date format. Please use YYYY-MM-DD HH:MM:SS'
                    ]
                )

# -----------------------------------------------------------------------------
# Class-Based Test for CustomDateTimeField
# -----------------------------------------------------------------------------
class TestCustomDateTimeField(BaseTestCase):
    def test_empty_date(self):
        class TestForm(Form):
            test_field = CustomDateTimeField(
                label='Test Field',
                error_messages={
                    'required': 'Date is required',
                    'invalid_format': 'Invalid date format',
                    'invalid_date': 'Invalid date values',
                    'invalid_time': 'Invalid time values',
                    'past_date': 'Date must be a future date',
                    'future_date': 'Date cannot be more than 5 years in the future',
                    'invalid_leap_year': 'Invalid date values (e.g., Feb 29 in non-leap years)'
                }
            )

        form = TestForm()
        self.assertFormInvalid(
            form, {'test_field': ''},
            {'test_field': ['Date is required']}
        )

    def test_invalid_date_format(self):
        class TestForm(Form):
            test_field = CustomDateTimeField(
                error_messages={
                    'invalid_format': 'Invalid date values'
                }
            )

        form = TestForm()
        self.assertFormInvalid(
            form, {'test_field': '2023-13-01 00:00:00'},
            {'test_field': ['Invalid date values']}
        )

    def test_invalid_time_values(self):
        class TestForm(Form):
            test_field = CustomDateTimeField(
                error_messages={
                    'invalid_time': 'Invalid time values'
                }
            )

        # Checking a single invalid time manually
        form = TestForm()
        form.test_field.process_formdata(['2023-01-01 25:00:00'])
        assert form.validate() is False
        assert 'Invalid time values' in form.test_field.errors

        # Test other invalid time cases in a loop
        invalid_times = [
            '2023-01-01 24:00:00',
            '2023-01-01 23:60:00',
            '2023-01-01 23:59:60',
        ]
        for time_str in invalid_times:
            form = TestForm()
            form.test_field.process_formdata([time_str])
            assert form.validate() is False
            assert 'Invalid time values' in form.test_field.errors

    def test_past_date(self):
        # We'll skip implementing a direct form-based test here since it's covered thoroughly
        pass

    def test_future_date_limit(self):
        class TestForm(Form):
            test_field = CustomDateTimeField(
                error_messages={
                    'future_date': 'Date cannot be more than 5 years in the future'
                }
            )
        form = TestForm()
        future_date = datetime.now().replace(year=datetime.now().year + 6)
        self.assertFormInvalid(
            form, {'test_field': future_date.strftime('%Y-%m-%d %H:%M:%S')},
            {'test_field': ['Date cannot be more than 5 years in the future']}
        )

    def test_leap_year_validation(self):
        class TestForm(Form):
            test_field = CustomDateTimeField(
                error_messages={
                    'invalid_leap_year': FlashMessages.INVALID_LEAP_YEAR
                }
            )

        # Test invalid leap year date
        form = TestForm()
        form.test_field.process_formdata(['2023-02-29 00:00:00'])
        assert form.validate() is False
        assert FlashMessages.INVALID_LEAP_YEAR in form.test_field.errors

        # Test valid leap year date
        form = TestForm()
        form.test_field.process_formdata(['2024-02-29 00:00:00'])
        assert form.validate() is True

# -----------------------------------------------------------------------------
# Simple Leap Year Validation (Outside Class)
# -----------------------------------------------------------------------------
def test_leap_year_validation(app):
    """Test leap year validation directly on CustomDateTimeField."""
    with app.test_request_context():
        field = CustomDateTimeField(
            error_messages={
                'invalid_leap_year': FlashMessages.INVALID_LEAP_YEAR
            }
        )

        # Valid leap year date
        field.process_formdata(['2024-02-29 12:00:00'])
        assert field.validate(None) is True
        assert field.errors == []

        # Invalid leap year date
        field.process_formdata(['2023-02-29 12:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_LEAP_YEAR in field.errors

# -----------------------------------------------------------------------------
# Test Error Messages from Constants
# -----------------------------------------------------------------------------
def test_error_messages_from_constants(app):
    """Test that error messages are using constants."""
    with app.test_request_context():
        field = CustomDateTimeField(
            error_messages={
                'required': FlashMessages.DATE_REQUIRED,
                'invalid_format': FlashMessages.INVALID_DATE_FORMAT,
                'invalid_time': FlashMessages.INVALID_TIME_VALUES,
                'invalid_leap_year': FlashMessages.INVALID_LEAP_YEAR
            }
        )

        # Empty date
        field.process_formdata([''])
        assert field.validate(None) is False
        assert FlashMessages.DATE_REQUIRED in field.errors

        # Invalid format
        field.process_formdata(['2023/02/28 12:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_DATE_FORMAT in field.errors

        # Invalid time
        field.process_formdata(['2023-02-28 25:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_TIME_VALUES in field.errors

        # Invalid leap year
        field.process_formdata(['2023-02-29 12:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_LEAP_YEAR in field.errors

# -----------------------------------------------------------------------------
# CustomDateTimeField Initialization
# -----------------------------------------------------------------------------
def test_custom_datetime_field_initialization(app):
    """Test CustomDateTimeField initialization with custom format."""
    with app.test_request_context():
        field = CustomDateTimeField(format='%Y/%m/%d %H:%M')
        assert field.format == '%Y/%m/%d %H:%M'
        assert field.render_kw == {'placeholder': 'YYYY-MM-DD HH:MM:SS'}

# -----------------------------------------------------------------------------
# Stipend CRUD Tests
# -----------------------------------------------------------------------------
def test_stipend_create_operation(app, form_data, test_db):
    """Test CRUD create operation."""
    with app.test_request_context():
        form = StipendForm()
        csrf_token = form.csrf_token.current_token
        form_data['csrf_token'] = csrf_token

        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]

        # Test valid creation
        form = StipendForm(data=form_data, meta={'csrf': False})
        form.tags.choices = tag_choices
        if not form.validate():
            print("Validation errors:", form.errors)
        assert form.validate() is True

        # Test missing required fields
        for field in ['name', 'summary', 'description']:
            invalid_data = form_data.copy()
            del invalid_data[field]
            form = StipendForm(data=invalid_data)
            form.tags.choices = tag_choices
            assert form.validate() is False
            assert field in form.errors


def test_audit_log_on_create(app, form_data, test_db):
    """Test audit log creation on stipend create."""
    with app.test_request_context():
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]

        # Create stipend
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices
        if form.validate():
            stipend = Stipend(**form.data)
            db.session.add(stipend)
            db.session.commit()

            # Create update data
            update_data = {
                'name': 'Updated Stipend Name',
                'summary': 'Updated summary',
                'description': 'Updated description',
                'tags': [tag_choices[0][0]]  # Use first tag
            }
            stipend.update(update_data)

            # Verify audit logs
            logs = AuditLog.query.filter_by(object_type='Stipend', object_id=stipend.id).order_by(AuditLog.timestamp.desc()).all()
            assert len(logs) >= 2  # create + update

            # Most recent log
            update_log = logs[0]
            assert update_log.action == 'update_stipend'
            assert update_log.details_before is not None
            assert update_log.details_after is not None

            # Previous log
            create_log = logs[1]
            assert create_log.action == 'create_stipend'
            assert create_log.details_after is not None


def test_stipend_update_operation(app, form_data, test_db):
    """Test CRUD update operation."""
    with app.test_request_context():
        form = StipendForm()
        csrf_token = form.csrf_token.current_token
        form_data['csrf_token'] = csrf_token

        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]

        # Create initial stipend
        form = StipendForm(data=form_data, meta={'csrf': False})
        form.tags.choices = tag_choices
        deadline = datetime.strptime(form.application_deadline.data, '%Y-%m-%d %H:%M:%S')

        # Create stipend via service
        stipend = Stipend.create({
            'name': form.name.data,
            'summary': form.summary.data,
            'description': form.description.data,
            'homepage_url': form.homepage_url.data,
            'application_procedure': form.application_procedure.data,
            'eligibility_criteria': form.eligibility_criteria.data,
            'application_deadline': deadline,
            'organization_id': form.organization_id.data,
            'open_for_applications': form.open_for_applications.data,
            'tags': [Tag.query.get(tid) for tid in form.tags.data]
        }, user_id=1)

        # Update stipend
        updated_data = form_data.copy()
        updated_data['name'] = 'Updated Stipend Name'
        updated_data['tags'] = [tag_choices[0][0]]  # first tag

        update_form = StipendForm(data=updated_data, meta={'csrf': False})
        update_form.tags.choices = tag_choices

        if not update_form.validate():
            print("Validation errors:", update_form.errors)
        assert update_form.validate() is True

        stipend.update({
            'name': update_form.name.data,
            'summary': update_form.summary.data,
            'description': update_form.description.data,
            'tags': [Tag.query.get(tid) for tid in update_form.tags.data]
        }, user_id=1)

        logs = AuditLog.query.filter_by(object_type='Stipend', object_id=stipend.id).order_by(AuditLog.timestamp.desc()).all()
        assert len(logs) >= 2

        update_log = logs[0]
        assert update_log.action == 'update_stipend'
        assert update_log.details_before is not None
        assert update_log.details_after is not None

        create_log = logs[1]
        assert create_log.action == 'create_stipend'
        assert create_log.details_after is not None

# -----------------------------------------------------------------------------
# Additional Validation on Create/Update
# -----------------------------------------------------------------------------
def filter_model_fields(data, model_class):
    """Filter out form fields that don't exist in the model."""
    return {k: v for k, v in data.items() if hasattr(model_class, k)}


def test_stipend_update_operation_extra(app, form_data, test_db):
    """Test CRUD update operation with additional validation checks."""
    with app.test_request_context():
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]

        # Test invalid date format
        invalid_data = form_data.copy()
        invalid_data['application_deadline'] = 'invalid-date'
        with pytest.raises(ValueError) as exc_info:
            Stipend.create(invalid_data)
        assert "Invalid date format" in str(exc_info.value)

        # Test past date
        invalid_data = form_data.copy()
        invalid_data['application_deadline'] = '2020-01-01 00:00:00'
        with pytest.raises(ValueError) as exc_info:
            Stipend.create(invalid_data)
        assert "Application deadline must be a future date" in str(exc_info.value)

        # Test future date limit
        invalid_data = form_data.copy()
        invalid_data['application_deadline'] = '2030-01-01 00:00:00'
        with pytest.raises(ValueError) as exc_info:
            Stipend.create(invalid_data)
        assert "Application deadline cannot be more than 5 years in the future" in str(exc_info.value)

        # Test invalid time values
        invalid_data = form_data.copy()
        invalid_data['application_deadline'] = '2025-12-31 25:00:00'
        with pytest.raises(ValueError) as exc_info:
            Stipend.create(invalid_data)
        assert "Invalid date format" in str(exc_info.value)

        # Test invalid organization ID
        invalid_data = form_data.copy()
        invalid_data['organization_id'] = 99999
        with pytest.raises(ValueError) as exc_info:
            Stipend.create(invalid_data)
        assert "Invalid organization ID" in str(exc_info.value)

        # Create a valid stipend
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices
        from pytz import utc
        deadline = utc.localize(datetime.strptime(form.application_deadline.data, '%Y-%m-%d %H:%M:%S'))

        stipend = Stipend.create({
            'name': form.name.data,
            'summary': form.summary.data,
            'description': form.description.data,
            'homepage_url': form.homepage_url.data,
            'application_procedure': form.application_procedure.data,
            'eligibility_criteria': form.eligibility_criteria.data,
            'application_deadline': deadline,
            'organization_id': form.organization_id.data,
            'open_for_applications': form.open_for_applications.data,
            'tags': [Tag.query.get(tid) for tid in form.tags.data]
        }, user_id=1)

        # Valid update
        updated_data = {
            'name': 'Updated Stipend Name',
            'summary': 'Updated summary',
            'description': 'Updated description',
            'tags': [Tag.query.get(tag_choices[0][0])]
        }
        updated_stipend = stipend.update(updated_data, user_id=1)
        assert updated_stipend.name == 'Updated Stipend Name'
        assert updated_stipend.summary == 'Updated summary'
        assert updated_stipend.description == 'Updated description'
        assert len(updated_stipend.tags) == 1

        # Invalid update missing name
        invalid_data = updated_data.copy()
        del invalid_data['name']
        with pytest.raises(ValueError) as exc_info:
            stipend.update(invalid_data, user_id=1)
        assert "Name is required" in str(exc_info.value)

# -----------------------------------------------------------------------------
# Delete Operation
# -----------------------------------------------------------------------------
def test_stipend_delete_operation(app, form_data, test_db):
    """Test CRUD delete operation."""
    with app.test_request_context():
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices

        model_data = form.data.copy()
        model_data['tags'] = [Tag.query.get(tid) for tid in form.tags.data]

        if 'application_deadline' in model_data:
            model_data['application_deadline'] = datetime.strptime(
                model_data['application_deadline'], '%Y-%m-%d %H:%M:%S'
            )

        model_data = filter_model_fields(model_data, Stipend)
        stipend = Stipend(**model_data)

        test_db.session.add(stipend)
        test_db.session.commit()
        assert Stipend.query.count() == 1

        Stipend.delete(stipend.id, user_id=1)
        assert Stipend.query.count() == 0

        log = AuditLog.query.filter_by(object_type='Stipend', object_id=stipend.id).first()
        assert log is not None
        assert log.action == 'delete_stipend'
        assert log.details is not None

# -----------------------------------------------------------------------------
# Utility Function Tests
# -----------------------------------------------------------------------------
def test_utils_format_error_message():
    from app.utils import format_error_message

    class TestField:
        def __init__(self, name, label=None):
            self.name = name
            self.label = label

    field = TestField('test_field', 'Test Field')
    error = 'Invalid value'
    assert format_error_message(field, error) == 'Test Field: Invalid value'

    field = TestField('test_field')
    assert format_error_message(field, error) == 'test_field: Invalid value'

    assert format_error_message('test_field', error) == 'test_field: Invalid value'
    assert format_error_message(field, 'invalid_format') == 'Invalid format'

# -----------------------------------------------------------------------------
# Base Service Tests
# -----------------------------------------------------------------------------
def test_base_service_create():
    from app.services.base_service import BaseService
    from app.models.stipend import Stipend

    class TestService(BaseService):
        def __init__(self):
            super().__init__(Stipend)

    service = TestService()

    data = {
        'name': 'Test Stipend',
        'summary': 'Test summary',
        'description': 'Test description',
        'homepage_url': 'https://example.com',
        'application_procedure': 'Test procedure',
        'eligibility_criteria': 'Test criteria',
        'application_deadline': '2025-12-31 23:59:59',
        'open_for_applications': True
    }
    stipend = service.create(data)
    assert stipend.id is not None

    invalid_data = data.copy()
    invalid_data['name'] = ''
    with pytest.raises(ValueError):
        service.create(invalid_data)
