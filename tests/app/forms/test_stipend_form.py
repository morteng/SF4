import pytest
from datetime import datetime, timedelta
from flask_wtf.csrf import generate_csrf
from app import create_app
from app.forms.admin_forms import StipendForm
from app.models.organization import Organization
from app.models.tag import Tag
from app.models.stipend import Stipend
from app.models.audit_log import AuditLog
from app.extensions import db
from app.forms.fields import CustomDateTimeField
from wtforms import Form, StringField

@pytest.fixture
def app():
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_db(app):
    return db

@pytest.fixture
def form_data(app):
    # Create a test organization and tag within application context
    with app.app_context():
        # Clean up existing test data
        db.session.query(Tag).filter(Tag.name == "Test Tag").delete()
        db.session.query(Organization).filter(Organization.name == "Test Org").delete()
        db.session.commit()

        # Create new test data
        org = Organization(name="Test Org", description="Test Description", homepage_url="https://test.org")
        tag = Tag(name="Test Tag", category="Test Category")
        db.session.add(org)
        db.session.add(tag)
        db.session.commit()

        # Generate CSRF token inside a test request context
        with app.test_request_context():
            csrf_token = generate_csrf()

        return {
            'name': 'Test Stipend',
            'summary': 'Test summary',
            'description': 'Test description',
            'homepage_url': 'https://example.com',
            'application_procedure': 'Test procedure',
            'eligibility_criteria': 'Test criteria',
            'organization_id': org.id,
            'tags': [tag.id],  # Add the required tag
            'open_for_applications': True,
            'csrf_token': csrf_token  # Add CSRF token
        }

def test_valid_date_format(app, form_data, test_db):
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

        # Get tag choices from database
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        # Validate the form
        form = StipendForm(data=form_data, meta={'csrf': False})
        form.tags.choices = tag_choices  # Set the choices
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
        assert 'Date is required' in form.errors['application_deadline']

class TestCustomDateTimeField(Form):
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
        field = TestCustomDateTimeField().test_field

        # Test with a valid leap year date
        field.process_formdata(['2028-02-29 12:00:00'])
        assert field.validate(TestCustomDateTimeField()) is True
        assert field.errors == []

        # Reset errors for next test
        field.errors = []

        # Test with an invalid leap year date
        field.process_formdata(['2023-02-29 12:00:00'])
        assert field.validate(TestCustomDateTimeField()) is False
        assert 'Invalid date values (e.g., Feb 29 in non-leap years)' in field.errors

def test_stipend_create_operation(app, form_data, test_db):
    """Test CRUD create operation"""
    with app.test_request_context():
        # Get tag choices from database
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        # Test valid creation
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices
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
            
            # Verify audit log
            log = AuditLog.query.filter_by(object_type='Stipend', object_id=stipend.id).first()
            assert log is not None
            assert log.action == 'create'
            assert log.details is not None

def test_stipend_update_operation(app, form_data, test_db):
    """Test CRUD update operation"""
    with app.test_request_context():
        # Get tag choices from database
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        # Create initial stipend
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices
        stipend = Stipend(**form.data)
        db.session.add(stipend)
        db.session.commit()
        
        # Update stipend
        updated_data = form_data.copy()
        updated_data['name'] = 'Updated Stipend Name'
        updated_data['tags'] = [tag_choices[0][0]]  # Use first tag
        
        update_form = StipendForm(data=updated_data)
        update_form.tags.choices = tag_choices
        assert update_form.validate() is True
        
        # Verify audit log
        log = AuditLog.query.filter_by(object_type='Stipend', object_id=stipend.id).first()
        assert log is not None
        assert log.action == 'update'
        assert log.details is not None

def test_stipend_delete_operation(app, form_data, test_db):
    """Test CRUD delete operation"""
    with app.test_request_context():
        # Get tag choices from database
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        # Create stipend
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices
        stipend = Stipend(**form.data)
        db.session.add(stipend)
        db.session.commit()
        
        # Delete stipend
        db.session.delete(stipend)
        db.session.commit()
        
        # Verify audit log
        log = AuditLog.query.filter_by(object_type='Stipend', object_id=stipend.id).first()
        assert log is not None
        assert log.action == 'delete'
        assert log.details is not None
