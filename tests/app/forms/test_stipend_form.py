# This file has been split into:
# - test_stipend_validation.py
# - test_stipend_crud.py
# - test_stipend_audit_logging.py

from datetime import datetime, timedelta
import pytest
from freezegun import freeze_time
from flask_wtf.csrf import generate_csrf
from app.models import Organization, Tag, Stipend, AuditLog
from app.forms.admin_forms import StipendForm
from app.forms.fields import CustomDateTimeField
from app.constants import FlashMessages
from app.extensions import db
from wtforms import Form
from tests.base_test_case import BaseTestCase

from freezegun import freeze_time

@freeze_time("2024-01-01 00:00:00")  # Mock the current date/time
@freeze_time("2024-01-01 00:00:00")  # Mock the current date/time
def test_valid_date_format(app, form_data, test_db):
    """Test valid date format"""
    valid_dates = [
        '2025-12-31 23:59:59',  # Standard valid date
        '2024-02-29 12:00:00',  # Leap year date
        '2025-01-01 00:00:00',  # Start of year
        '2025-12-31 00:00:00',  # End of year
        '2025-06-15 12:30:45'   # Mid-year with specific time
    ]
    
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

        # Get tag choices from database
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        # Test each valid date format
        for date in valid_dates:
            form_data['application_deadline'] = date
            form = StipendForm(data=form_data, meta={'csrf': False})
            form.tags.choices = tag_choices  # Set the choices
            if not form.validate():
                print(f"Validation errors for {date}:", form.errors)
            assert form.validate() is True, f"Failed validation for date: {date}"

def test_invalid_date_format(app, form_data, test_db):
    """Test invalid date formats"""
    invalid_dates = [
        '2025-12-31',  # Missing time
        '2025-12-31 25:00:00',  # Invalid hour
        '2025-02-30 12:00:00',  # Invalid date
        'invalid-date',  # Completely invalid
    ]

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

        # Get tag choices from database
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]

        # Test each invalid date format
        for date in invalid_dates:
            form_data['application_deadline'] = date
            form = StipendForm(data=form_data, meta={'csrf': False})
            form.tags.choices = tag_choices  # Set the choices
            assert form.validate() is False, f"Expected validation failure for date: {date}"
            assert 'application_deadline' in form.errors, f"Expected application_deadline error for date: {date}"
    
    with app.test_request_context():
        # Add CSRF token to form data
        form_data['csrf_token'] = generate_csrf()
        
        # Get tag choices from database
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
            
        for date in invalid_dates:
            form_data['application_deadline'] = date
            form = StipendForm(data=form_data)
            form.tags.choices = tag_choices  # Set the choices
            assert form.validate() is False
            assert 'application_deadline' in form.errors

def test_past_date(app, form_data):
    """Test past date validation"""
    yesterday = datetime.now() - timedelta(days=1)
    form_data['application_deadline'] = yesterday.strftime('%Y-%m-%d %H:%M:%S')
    with app.test_request_context():
        # Get tag choices from database
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
            
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices  # Set the choices
        assert form.validate() is False
        assert 'Application deadline must be a future date' in form.errors['application_deadline']

def test_future_date_limit(app, form_data, test_db):
    """Test future date limit (5 years)"""
    # Import models first
    from app.models import Tag, Organization

    # Clean the database before starting
    db.session.query(Tag).delete()
    db.session.query(Organization).delete()
    db.session.commit()

    # Create test tags and organizations
    tag = Tag(name="Test Tag", category="Test Category")
    org = Organization(name="Test Org", description="Test Description", homepage_url="https://test.org")
    db.session.add(tag)
    db.session.add(org)
    db.session.commit()

    future_date = datetime.now().replace(year=datetime.now().year + 6)
    form_data['application_deadline'] = future_date.strftime('%Y-%m-%d %H:%M:%S')
    with app.test_request_context():
        # Get tag choices from database
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
            
        # Initialize form with choices
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices
            
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
        # Get tag choices from database
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
            
        for time in invalid_times:
            form_data['application_deadline'] = time
            form = StipendForm(data=form_data)
            form.tags.choices = tag_choices  # Set the choices
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

def test_missing_required_fields(app, form_data):
    """Test validation of all required fields."""
    required_fields = [
        'name', 'summary', 'description', 'homepage_url',
        'application_procedure', 'eligibility_criteria',
        'application_deadline', 'organization_id'
    ]
    
    # Test empty strings
    with app.test_request_context():
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        for field in required_fields:
            if field != 'organization_id':  # Skip organization_id as it's a SelectField
                invalid_data = form_data.copy()
                invalid_data[field] = ''  # Set to empty string
                
                form = StipendForm(data=invalid_data, meta={'csrf': False})
                form.tags.choices = tag_choices
                assert form.validate() is False, f"Form should be invalid when {field} is empty"
                assert field in form.errors, f"Expected error for empty {field} but got: {form.errors}"
    
    # Test missing fields
    with app.test_request_context():
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        for field in required_fields:
            invalid_data = form_data.copy()
            del invalid_data[field]
    
            form = StipendForm(data=invalid_data, meta={'csrf': False})
            form.tags.choices = tag_choices
            if field == 'organization_id':
                form.organization_id.choices = [(1, 'Test Org')]  # Add dummy choice
            assert form.validate() is False, f"Form should be invalid when {field} is missing"
            assert field in form.errors, f"Expected error for missing {field} but got: {form.errors}"
            
            # Special check for application_deadline
            if field == 'application_deadline':
                assert any(msg in form.errors['application_deadline'] 
                         for msg in ['Application deadline is required.', 
                                    'Invalid date format. Please use YYYY-MM-DD HH:MM:SS'])

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
        
        form = TestForm()
        form.test_field.process_formdata(['2023-01-01 25:00:00'])
        assert form.validate() is False
        assert 'Invalid time values' in form.test_field.errors
        
        # Test other invalid time cases
        invalid_times = [
            '2023-01-01 24:00:00',  # Invalid hour
            '2023-01-01 23:60:00',  # Invalid minute
            '2023-01-01 23:59:60',  # Invalid second
        ]
        
        for time in invalid_times:
            form = TestForm()
            form.test_field.process_formdata([time])
            assert form.validate() is False
            assert 'Invalid time values' in form.test_field.errors

    def test_past_date(self):
        field = CustomDateTimeField()
        self.assertFormInvalid(
            field, {'': '2020-01-01 00:00:00'},  # Past date
            {'': ['Date must be a future date']}
        )

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
        form.test_field.process_formdata(['2024-02-29 00:00:00'])  # 2024 is a leap year
        assert form.validate() is True

def test_leap_year_validation(app):
    """Test leap year validation directly on CustomDateTimeField."""
    with app.test_request_context():
        field = CustomDateTimeField(
            error_messages={
                'invalid_leap_year': FlashMessages.INVALID_LEAP_YEAR
            }
        )

        # Test with a valid leap year date
        field.process_formdata(['2024-02-29 12:00:00'])
        assert field.validate(None) is True
        assert field.errors == []

        # Test with an invalid leap year date
        field.process_formdata(['2023-02-29 12:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_LEAP_YEAR in field.errors

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

        # Test empty date
        field.process_formdata([''])
        assert field.validate(None) is False
        assert FlashMessages.DATE_REQUIRED in field.errors

        # Test invalid format
        field.process_formdata(['2023/02/28 12:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_DATE_FORMAT in field.errors

        # Test invalid time
        field.process_formdata(['2023-02-28 25:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_TIME_VALUES in field.errors

        # Test invalid leap year
        field.process_formdata(['2023-02-29 12:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_LEAP_YEAR in field.errors

def test_leap_year_validation_simplified(app):
    """Test leap year validation directly on CustomDateTimeField."""
    with app.test_request_context():
        field = CustomDateTimeField(
            error_messages={
                'invalid_leap_year': FlashMessages.INVALID_LEAP_YEAR
            }
        )

        # Test with a valid leap year date
        field.process_formdata(['2024-02-29 12:00:00'])
        assert field.validate(None) is True
        assert field.errors == []

        # Test with an invalid leap year date
        field.process_formdata(['2023-02-29 12:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_LEAP_YEAR in field.errors

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

        # Test empty date
        field.process_formdata([''])
        assert field.validate(None) is False
        assert FlashMessages.DATE_REQUIRED in field.errors

        # Test invalid format
        field.process_formdata(['2023/02/28 12:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_DATE_FORMAT in field.errors

        # Test invalid time
        field.process_formdata(['2023-02-28 25:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_TIME_VALUES in field.errors

        # Test invalid leap year
        field.process_formdata(['2023-02-29 12:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_LEAP_YEAR in field.errors

def test_custom_datetime_field_initialization(app):
    """Test CustomDateTimeField initialization with custom format."""
    with app.test_request_context():
        field = CustomDateTimeField(format='%Y/%m/%d %H:%M')
        assert field.format == '%Y/%m/%d %H:%M'
        assert field.render_kw == {'placeholder': 'YYYY-MM-DD HH:MM:SS'}

def test_invalid_time_components(app):
    """Test validation of invalid time components."""
    with app.test_request_context():
        field = CustomDateTimeField()
        
        # Test invalid hour
        field.process_formdata(['2023-02-28 24:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_TIME_VALUES in field.errors
        
        # Test invalid minute
        field.process_formdata(['2023-02-28 23:60:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_TIME_VALUES in field.errors
        
        # Test invalid second
        field.process_formdata(['2023-02-28 23:59:60'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_TIME_VALUES in field.errors

def test_invalid_time_components(app):
    """Test validation of invalid time components."""
    with app.test_request_context():
        field = CustomDateTimeField()
        
        # Test invalid hour
        field.process_formdata(['2023-02-28 24:00:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_TIME_VALUES in field.errors
        
        # Test invalid minute
        field.process_formdata(['2023-02-28 23:60:00'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_TIME_VALUES in field.errors
        
        # Test invalid second
        field.process_formdata(['2023-02-28 23:59:60'])
        assert field.validate(None) is False
        assert FlashMessages.INVALID_TIME_VALUES in field.errors

def test_stipend_create_operation(app, form_data, test_db):
    """Test CRUD create operation"""
    with app.test_request_context():
        # Generate valid CSRF token
        form = StipendForm()
        csrf_token = form.csrf_token.current_token
        form_data['csrf_token'] = csrf_token
        
        # Get tag choices from database
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
    """Test audit log creation on stipend create"""
    with app.test_request_context():
        # Get tag choices from database
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
            
            # Update the stipend
            stipend.update(update_data)
            
            # Verify audit logs
            logs = AuditLog.query.filter_by(object_type='Stipend', object_id=stipend.id).order_by(AuditLog.timestamp.desc()).all()
            assert len(logs) >= 2  # Should have create and update logs
            
            # Verify update log
            update_log = logs[0]
            assert update_log is not None
            assert update_log.action == 'update_stipend'
            assert update_log.details_before is not None
            assert update_log.details_after is not None
            
            # Verify create log
            create_log = logs[1]
            assert create_log is not None
            assert create_log.action == 'create_stipend'
            assert create_log.details_after is not None

def test_stipend_update_operation(app, form_data, test_db):
    """Test CRUD update operation"""
    with app.test_request_context():
        # Generate valid CSRF token
        form = StipendForm()
        csrf_token = form.csrf_token.current_token
        form_data['csrf_token'] = csrf_token
        
        # Get tag choices from database
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        # Create initial stipend
        form = StipendForm(data=form_data, meta={'csrf': False})
        form.tags.choices = tag_choices
        
        # Convert string date to datetime object
        from datetime import datetime
        deadline = datetime.strptime(form.application_deadline.data, '%Y-%m-%d %H:%M:%S')
            
        # Create stipend using service layer
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
            'tags': [Tag.query.get(tag_id) for tag_id in form.tags.data]
        }, user_id=1)  # Provide a valid user_id for testing
        
        # Update stipend
        updated_data = form_data.copy()
        updated_data['name'] = 'Updated Stipend Name'
        updated_data['tags'] = [tag_choices[0][0]]  # Use first tag
        
        update_form = StipendForm(data=updated_data, meta={'csrf': False})
        update_form.tags.choices = tag_choices
        
        if not update_form.validate():
            print("Validation errors:", update_form.errors)
        assert update_form.validate() is True
        
        # Perform the update with user_id
        stipend.update({
            'name': update_form.name.data,
            'summary': update_form.summary.data,
            'description': update_form.description.data,
            'tags': [Tag.query.get(tag_id) for tag_id in update_form.tags.data]
        }, user_id=1)
            
        # Verify audit logs
        logs = AuditLog.query.filter_by(object_type='Stipend', object_id=stipend.id).order_by(AuditLog.timestamp.desc()).all()
        assert len(logs) >= 2  # Should have create and update logs
            
        # Verify update log
        update_log = logs[0]
        assert update_log is not None
        assert update_log.action == 'update_stipend'
        assert update_log.details_before is not None
        assert update_log.details_after is not None
            
        # Verify create log
        create_log = logs[1]
        assert create_log is not None
        assert create_log.action == 'create_stipend'
        assert create_log.details_after is not None

def filter_model_fields(data, model_class):
    """Filter out form fields that don't exist in the model"""
    return {k: v for k, v in data.items() if hasattr(model_class, k)}

def test_stipend_update_operation(app, form_data, test_db):
    """Test CRUD update operation with validation"""
    with app.test_request_context():
        # Get tag choices from database
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        # Test invalid date format
        invalid_data = form_data.copy()
        invalid_data['application_deadline'] = 'invalid-date'
        with pytest.raises(ValueError) as exc_info:
            Stipend.create(invalid_data)
        assert "Invalid date format" in str(exc_info.value)
        
        # Test past date validation
        invalid_data = form_data.copy()
        invalid_data['application_deadline'] = '2020-01-01 00:00:00'
        with pytest.raises(ValueError) as exc_info:
            Stipend.create(invalid_data)
        assert "Application deadline must be a future date" in str(exc_info.value)
        
        # Test future date limit (5 years)
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
        
        # Create initial stipend
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices
        
        # Convert application_deadline to datetime and localize to UTC
        from datetime import datetime
        from pytz import utc
        deadline = utc.localize(datetime.strptime(form.application_deadline.data, '%Y-%m-%d %H:%M:%S'))
        
        # Create stipend
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
            'tags': [Tag.query.get(tag_id) for tag_id in form.tags.data]
        }, user_id=1)
        
        # Test valid update
        updated_data = {
            'name': 'Updated Stipend Name',
            'summary': 'Updated summary',
            'description': 'Updated description',
            'tags': [Tag.query.get(tag_choices[0][0])]  # Convert ID to Tag instance
        }
        updated_stipend = stipend.update(updated_data, user_id=1)
        
        assert updated_stipend.name == 'Updated Stipend Name'
        assert updated_stipend.summary == 'Updated summary'
        assert updated_stipend.description == 'Updated description'
        assert len(updated_stipend.tags) == 1
        
        # Test invalid update with missing required field
        invalid_data = updated_data.copy()
        del invalid_data['name']
        with pytest.raises(ValueError) as exc_info:
            stipend.update(invalid_data, user_id=1)
        assert "Name is required" in str(exc_info.value)

def test_stipend_delete_operation(app, form_data, test_db):
    """Test CRUD delete operation"""
    with app.test_request_context():
        # Get tag choices from database
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        # Create stipend
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices
        
        # Convert tag IDs to Tag instances
        model_data = form.data.copy()
        model_data['tags'] = [Tag.query.get(tag_id) for tag_id in form.tags.data]
            
        # Convert string dates to datetime objects
        from datetime import datetime
        if 'application_deadline' in model_data:
            model_data['application_deadline'] = datetime.strptime(
                model_data['application_deadline'], '%Y-%m-%d %H:%M:%S'
            )
    
        # Filter out non-model fields
        model_data = filter_model_fields(model_data, Stipend)
    
        # Create stipend instance
        stipend = Stipend(**model_data)
        
        # Save to database
        test_db.session.add(stipend)
        test_db.session.commit()
        
        # Verify creation
        assert Stipend.query.count() == 1
        
        # Delete stipend with audit logging
        Stipend.delete(stipend.id, user_id=1)
        
        # Verify deletion
        assert Stipend.query.count() == 0
        
        # Verify audit log
        log = AuditLog.query.filter_by(object_type='Stipend', object_id=stipend.id).first()
        assert log is not None
        assert log.action == 'delete_stipend'
        assert log.details is not None
def test_utils_format_error_message():
    from app.utils import format_error_message
    
    # Test with field object
    class TestField:
        def __init__(self, name, label=None):
            self.name = name
            self.label = label
    
    field = TestField('test_field', 'Test Field')
    error = 'Invalid value'
    assert format_error_message(field, error) == 'Test Field: Invalid value'
    
    # Test with field name only
    field = TestField('test_field')
    assert format_error_message(field, error) == 'test_field: Invalid value'
    
    # Test with string field
    assert format_error_message('test_field', error) == 'test_field: Invalid value'
    
    # Test with mapped error
    assert format_error_message(field, 'invalid_format') == 'Invalid format'

def test_base_service_create():
    from app.services.base_service import BaseService
    from app.models.stipend import Stipend
    
    class TestService(BaseService):
        def __init__(self):
            super().__init__(Stipend)
    
    service = TestService()
    
    # Test valid creation
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
    
    # Test invalid data
    invalid_data = data.copy()
    invalid_data['name'] = ''
    with pytest.raises(ValueError):
        service.create(invalid_data)
