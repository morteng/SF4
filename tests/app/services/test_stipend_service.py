import pytest
import re  # Import the re module to use regex for extracting CSRF token
from wtforms.validators import ValidationError
from app.models.stipend import Stipend
from app.models.organization import Organization
from app.services.stipend_service import StipendService
from datetime import datetime
from flask_login import login_user
from app.extensions import db  # Ensure consistent session usage
from app.forms.admin_forms import StipendForm
from app.models.user import User
from app.constants import FlashMessages, FlashCategory
from flask import get_flashed_messages
import logging


def test_create_stipend_with_invalid_application_deadline_format(test_data, db_session, app, admin_user):
    # Test various invalid date formats
    invalid_formats = [
        '12/31/2023 23:59:59',  # Wrong format
        '2023-02-30 12:00:00',  # Invalid date
        '2023-13-01 12:00:00',  # Invalid month
        '2023-01-32 12:00:00',  # Invalid day
        '2023-01-01 25:00:00',  # Invalid hour
        '2023-01-01 12:60:00',  # Invalid minute
        '2023-01-01 12:00:60',  # Invalid second
        'invalid-date',         # Completely invalid
        '',                     # Empty string
        None                    # Null value
    ]
    
    for invalid_format in invalid_formats:
        test_data['application_deadline'] = invalid_format
        
        with app.app_context(), app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
            
            stipend_data = {k: v for k, v in test_data.items() if k != 'submit'}
            service = StipendService()
            
            with pytest.raises(ValueError) as exc_info:
                service.create(stipend_data)
            
            assert "Invalid date format" in str(exc_info.value)
            
            # Verify no record was created
            new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
            assert new_stipend is None

def test_create_stipend_with_missing_required_fields(test_data, db_session, app, admin_user):
    """Test creation with missing required fields"""
    required_fields = ['name', 'organization_id', 'application_deadline']
    
    for field in required_fields:
        invalid_data = test_data.copy()
        invalid_data.pop(field)
        
        with app.app_context(), app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
            
            service = StipendService()
            
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data)
            
            assert f"Missing required field: {field}" in str(exc_info.value)
            
            # Verify no record was created
            new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
            assert new_stipend is None

def test_create_stipend_with_invalid_organization(test_data, db_session, app, admin_user):
    """Test creation with invalid organization ID"""
    invalid_data = test_data.copy()
    invalid_data['organization_id'] = 99999  # Non-existent organization
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        
        with pytest.raises(ValueError) as exc_info:
            service.create(invalid_data)
        
        assert "Invalid organization" in str(exc_info.value)
        
        # Verify no record was created
        new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
        assert new_stipend is None

def test_create_stipend_with_invalid_tags(test_data, db_session, app, admin_user):
    """Test creation with invalid tag IDs"""
    invalid_data = test_data.copy()
    invalid_data['tags'] = [99999]  # Non-existent tag
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        
        with pytest.raises(ValueError) as exc_info:
            service.create(invalid_data)
        
        assert "Invalid tags" in str(exc_info.value)
        
        # Verify no record was created
        new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
        assert new_stipend is None

def test_create_stipend_with_past_deadline(test_data, db_session, app, admin_user):
    """Test creation with past deadline"""
    invalid_data = test_data.copy()
    invalid_data['application_deadline'] = '2020-01-01 00:00:00'  # Past date
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        
        with pytest.raises(ValueError) as exc_info:
            service.create(invalid_data)
        
        assert "Deadline must be in the future" in str(exc_info.value)
        
        # Verify no record was created
        new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
        assert new_stipend is None

def test_create_stipend_with_max_length_fields(test_data, db_session, app, admin_user):
    """Test creation with maximum length fields"""
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    
    # Set max length values
    test_data.update({
        'name': 'A' * 100,  # Max length
        'summary': 'B' * 500,
        'description': 'C' * 2000,
        'homepage_url': 'http://' + 'a' * 200 + '.com',
        'application_procedure': 'D' * 2000,
        'eligibility_criteria': 'E' * 2000,
        'organization_id': org.id
    })

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.create(test_data)
        
        # Verify all fields were saved correctly
        stipend = Stipend.query.filter_by(name=test_data['name']).first()
        assert stipend is not None
        assert len(stipend.name) == 100
        assert len(stipend.summary) == 500
        assert len(stipend.description) == 2000

def test_create_stipend_with_minimal_data(db_session, app, admin_user):
    """Test creation with only required fields"""
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    
    minimal_data = {
        'name': 'Minimal Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.create(minimal_data)
        
        # Verify stipend was created with minimal data
        stipend = Stipend.query.filter_by(name='Minimal Stipend').first()
        assert stipend is not None
        assert stipend.summary is None
        assert stipend.description is None

def test_update_stipend_with_empty_fields(test_data, db_session, app, admin_user):
    """Test updating with empty optional fields"""
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    update_data = {
        'name': 'Updated Stipend',
        'summary': '',
        'description': '',
        'organization_id': stipend.organization_id
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.update(stipend.id, update_data)
        
        # Verify update
        updated_stipend = Stipend.query.get(stipend.id)
        assert updated_stipend.name == 'Updated Stipend'
        assert updated_stipend.summary is None
        assert updated_stipend.description is None

def test_stipend_service_rate_limiting(test_data, app):
    """Test rate limiting in stipend service"""
    service = StipendService()
    
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    # Make 11 requests (limit is 10 per minute)
    with pytest.raises(Exception) as exc_info:
        for i in range(11):
            service.create(test_data)
            
    assert "Rate limit exceeded" in str(exc_info.value)

def test_stipend_service_audit_logging(test_data, db_session, app, admin_user):
    """Test audit logging in stipend service"""
    from app.models.audit_log import AuditLog
    
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.create(test_data)
        
        # Verify audit log was created
        log = AuditLog.query.filter_by(object_type='Stipend').first()
        assert log is not None
        assert log.action == 'create'
        assert log.object_id == result.id

def test_create_stipend_with_invalid_organization(test_data, db_session, app):
    """Test creating stipend with invalid organization"""
    test_data['organization_id'] = 9999  # Non-existent organization
    
    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
        
    assert "Invalid organization" in str(exc_info.value)

def test_update_stipend_with_invalid_data(test_data, db_session, app):
    """Test updating stipend with invalid data"""
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    invalid_data = {
        'name': '',  # Invalid name
        'application_deadline': 'invalid-date'
    }

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.update(stipend.id, invalid_data)
        
    errors = exc_info.value.args[0]
    assert 'name' in errors
    assert 'application_deadline' in errors

def test_delete_stipend_with_dependencies(test_data, db_session, app):
    """Test deleting stipend with dependent records"""
    from app.models.tag import Tag
    
    # Create stipend with tags
    stipend = Stipend(**test_data)
    tag = Tag(name="Test Tag")
    stipend.tags.append(tag)
    db.session.add(stipend)
    db.session.commit()

    service = StipendService()
    
    # Should still be able to delete
    result = service.delete(stipend.id)
    assert result is True
    
    # Verify deletion
    assert Stipend.query.get(stipend.id) is None
    assert Tag.query.get(tag.id) is not None  # Tags should remain

def test_create_stipend_with_duplicate_name(test_data, db_session, app):
    """Test creating stipend with duplicate name"""
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    # Create initial stipend
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
        
    assert "already exists" in str(exc_info.value)

def test_create_stipend_with_past_deadline(test_data, db_session, app):
    """Test creating stipend with past deadline"""
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id
    test_data['application_deadline'] = '2020-01-01 00:00:00'  # Past date

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
        
    assert "must be in the future" in str(exc_info.value)

def test_update_stipend_with_invalid_tags(test_data, db_session, app):
    """Test updating stipend with invalid tags"""
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    invalid_data = {
        'tags': [9999]  # Non-existent tag
    }

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.update(stipend.id, invalid_data)
        
    assert "Invalid tags" in str(exc_info.value)

def test_create_stipend_with_all_fields(test_data, db_session, app, admin_user):
    # Create an organization first
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    test_data['organization_id'] = org.id  # Use the created organization's ID

    # Convert datetime object to string for form submission
    test_data['application_deadline'] = test_data['application_deadline'].strftime('%Y-%m-%d %H:%M:%S')

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Create a form instance and validate it
        form = StipendForm(data=test_data)
        assert form.validate(), f"Form validation failed: {form.errors}"
        
        service = StipendService()
        result = service.create(form.data)

    # Query the stipend from the session to ensure it's bound
    new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()

    # Check if the stipend was created successfully with all fields
    assert new_stipend is not None
    for key, value in test_data.items():
        if key == 'application_deadline':
            assert new_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == value
        else:
            assert getattr(new_stipend, key) == value

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.CREATE_STIPEND_SUCCESS.value in messages

def test_create_stipend_with_missing_optional_fields(db_session, app, admin_user):
    # Create an organization first
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()

    test_data = {
        'name': "Test Stipend",
        'application_deadline': datetime.strptime('2023-12-31 23:59:59', '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),
        'open_for_applications': True,
        'organization_id': org.id  # Add the required organization_id
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Create a form instance and validate it
        form = StipendForm(data=test_data)
        assert form.validate(), f"Form validation failed: {form.errors}"
        
        service = StipendService()
        result = service.create(form.data)

    # Query the stipend from the session to ensure it's bound
    new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()

    # Check if the stipend was created successfully with missing optional fields
    assert new_stipend is not None
    assert new_stipend.name == test_data['name']
    assert new_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == test_data['application_deadline']
    assert new_stipend.open_for_applications is True
    assert new_stipend.summary is None  # Assuming summary is optional
    assert new_stipend.description is None  # Assuming description is optional
    assert new_stipend.organization_id == org.id  # Verify organization association

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.CREATE_STIPEND_SUCCESS.value in messages

def test_create_stipend_with_invalid_date_format(test_data, db_session, app, admin_user):
    # Modify test data with an invalid application_deadline format
    test_data['application_deadline'] = 'invalid-format'  # Different format

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        # Create a form instance and validate it
        form = StipendForm(data=test_data)
        
        service = StipendService()
        result = service.create(form.data)

    # Assert that the stipend was not created due to validation errors
    new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
    assert new_stipend is None

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.INVALID_DATE_FORMAT.value in messages

def test_update_stipend_with_valid_data(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()
    
    update_data = {
        'name': "Updated Test Stipend",
        'summary': 'Updated summary',
        'description': test_data['description'],
        'homepage_url': test_data['homepage_url'],
        'application_procedure': test_data['application_procedure'],
        'eligibility_criteria': test_data['eligibility_criteria'],
        'application_deadline': datetime.strptime('2024-12-31 23:59:59', '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),  # Ensure it's a string
        'open_for_applications': True
    }
    
    with app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
    
        # Use StipendForm to handle form submission
        form = StipendForm(data=update_data)
        assert form.validate(), f"Form validation failed: {form.errors}"
        # Simulate form submission to the edit route
        service = StipendService()
        result = service.update(stipend.id, form.data)
        assert result is not None  # Check service returned a result
        
        db.session.refresh(stipend)
    
    # Query the stipend from the session to ensure it's bound
    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
    
    # Check if the stipend was updated successfully
    assert updated_stipend is not None
    assert updated_stipend.name == "Updated Test Stipend"
    assert updated_stipend.summary == 'Updated summary'
    assert updated_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2024-12-31 23:59:59'
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.UPDATE_STIPEND_SUCCESS.value in messages

def test_update_stipend_with_invalid_application_deadline_format(test_data, db_session, app, admin_user):
    # Create initial stipend
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()
    
    # Test various invalid date formats
    invalid_formats = [
        '2024-13-32 99:99:99',  # Invalid everything
        '2023-02-30 12:00:00',  # Invalid day
        '2023-04-31 12:00:00',  # Invalid day
        '2023-00-01 12:00:00',  # Invalid month
        '2023-01-00 12:00:00',  # Invalid day
        'invalid-date',         # Completely invalid
        '',                     # Empty string
        None                    # Null value
    ]
    
    for invalid_format in invalid_formats:
        update_data = {
            'name': test_data['name'],
            'application_deadline': invalid_format,
        }
        
        with app.app_context(), app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
                
            form = StipendForm(data=update_data)
            service = StipendService()
            
            with pytest.raises(ValueError) as exc_info:
                service.update(stipend.id, form.data)
            
            assert "Invalid date format" in str(exc_info.value)
            
            # Verify stipend was not updated
            updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
            assert updated_stipend.application_deadline == test_data['application_deadline']

def test_update_stipend_open_for_applications(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    update_data = {
        'name': test_data['name'],  # Add the name field
        'summary': test_data['summary'],
        'description': test_data['description'],
        'homepage_url': test_data['homepage_url'],
        'application_procedure': test_data['application_procedure'],
        'eligibility_criteria': test_data['eligibility_criteria'],
        'application_deadline': test_data['application_deadline'].strftime('%Y-%m-%d %H:%M:%S'),
        'open_for_applications': True,
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Create a form instance and validate it
        form = StipendForm(data=update_data)
        assert form.validate(), f"Form validation failed: {form.errors}"
        # Simulate form submission after calling update_stipend
        service = StipendService()
        result = service.update(stipend.id, form.data)

    # Query the stipend from the session to ensure it's bound
    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()

    # Check if the stipend was updated successfully
    assert updated_stipend is not None
    assert updated_stipend.open_for_applications is True

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.UPDATE_STIPEND_SUCCESS.value in messages

def test_update_stipend_open_for_applications_as_string(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    update_data = {
        'name': test_data['name'],
        'summary': test_data['summary'],
        'description': test_data['description'],
        'homepage_url': test_data['homepage_url'],
        'application_procedure': test_data['application_procedure'],
        'eligibility_criteria': test_data['eligibility_criteria'],
        'application_deadline': test_data['application_deadline'].strftime('%Y-%m-%d %H:%M:%S'),
        'open_for_applications': 'yes',  # Pass as string
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Create a form instance and validate it
        form = StipendForm(data=update_data)
        assert form.validate(), f"Form validation failed: {form.errors}"
        
        # Simulate form submission after calling update_stipend
        service = StipendService()
        result = service.update(stipend.id, form.data)

    # Query the stipend from the session to ensure it's bound
    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()

    # Check if the stipend was updated successfully
    assert updated_stipend is not None
    assert updated_stipend.open_for_applications is True

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.UPDATE_STIPEND_SUCCESS.value in messages

def test_update_stipend_change_all_fields(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()
 
    update_data = {
        'name': "Updated All Fields",
        'summary': 'Updated summary for all fields',
        'description': 'Updated description for all fields.',
        'homepage_url': 'http://updated.com',
        'application_procedure': 'Updated procedure',
        'eligibility_criteria': 'Updated criteria',
        'application_deadline': datetime.strptime('2025-12-31 23:59:59', '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),
        'open_for_applications': '0'
    }
 
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Use StipendForm to handle form submission
        form = StipendForm(data=update_data)
        # Manually process the form to trigger the process_data method
        form.process()

        assert form.validate(), f"Form validation failed: {form.errors}"
        
        # Simulate form submission
        response = client.post(f'/admin/stipends/{stipend.id}/edit', data=form.data, follow_redirects=True)
 
    # Refresh the stipend object to get the updated data from the database
    db_session.refresh(stipend)
 
    # Query the stipend from the session to ensure it's bound
    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
 
    # Check if the stipend was updated successfully with all fields changed
    assert updated_stipend is not None
    for key, value in update_data.items():
        if key == 'application_deadline':
            assert updated_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == value
        else:
            assert getattr(updated_stipend, key) == False if key == 'open_for_applications' else getattr(updated_stipend, key) == value
 
    # Check if the correct flash message was set
    with app.test_request_context():
        assert FlashMessages.UPDATE_STIPEND_SUCCESS.encode() in response.data

def test_update_stipend_with_empty_application_deadline(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    update_data = {
        'name': test_data['name'],
        'application_deadline': '',  # Empty string
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Create a form instance and validate it
        form = StipendForm(data=update_data)
        assert not form.validate(), f"Form validation should have failed: {form.errors}"
        
        # Simulate form submission after calling update_stipend
        response = client.post(f'/admin/stipends/{stipend.id}/edit', data=form.data, follow_redirects=True)

    # Assert that the stipend was not updated due to validation errors
    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
    assert updated_stipend.application_deadline == test_data['application_deadline']  # Should remain unchanged

    # Check if the correct flash message was set
    with app.test_request_context():
        assert FlashMessages.INVALID_DATE_FORMAT.encode() in response.data

def test_delete_existing_stipend(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.delete(stipend.id)

    # Assert that the stipend was deleted
    deleted_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
    assert deleted_stipend is None

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.DELETE_STIPEND_SUCCESS.value in messages

def test_delete_nonexistent_stipend(app, admin_user):
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.delete(9999)  # Assuming there's no stipend with ID 9999

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.STIPEND_NOT_FOUND.value in messages

def test_get_stipend_by_valid_id(test_data, db_session, app):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    service = StipendService()
    retrieved_stipend = service.get_by_id(stipend.id)
    assert retrieved_stipend is not None
    assert retrieved_stipend.name == test_data['name']

def test_get_stipend_by_invalid_id(app):
    service = StipendService()
    retrieved_stipend = service.get_by_id(9999)  # Assuming there's no stipend with ID 9999
    assert retrieved_stipend is None

def test_get_all_stipends_with_multiple_entries(test_data, db_session, app):
    stipend1 = Stipend(**test_data)
    stipend2 = Stipend(name="Another Test Stipend", summary="Summary of another stipend")
    db_session.add(stipend1)
    db_session.add(stipend2)
    db_session.commit()

    service = StipendService()
    all_stipends = service.get_all()
    assert len(all_stipends) == 2
    assert any(s.name == test_data['name'] for s in all_stipends)

def test_get_all_stipends_with_no_entries(app):
    service = StipendService()
    all_stipends = service.get_all()
    assert len(all_stipends) == 0

def test_create_stipend_with_max_length_fields(test_data, db_session, app, admin_user):
    """Test creating stipend with maximum length fields"""
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    
    # Set max length values
    test_data.update({
        'name': 'A' * 100,  # Max length
        'summary': 'B' * 500,
        'description': 'C' * 2000,
        'homepage_url': 'http://' + 'a' * 200 + '.com',
        'application_procedure': 'D' * 2000,
        'eligibility_criteria': 'E' * 2000,
        'organization_id': org.id
    })

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.create(test_data)
        
        # Verify all fields were saved correctly
        stipend = Stipend.query.filter_by(name=test_data['name']).first()
        assert stipend is not None
        assert len(stipend.name) == 100
        assert len(stipend.summary) == 500
        assert len(stipend.description) == 2000

def test_create_stipend_with_minimal_data(db_session, app, admin_user):
    """Test creating stipend with only required fields"""
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    
    minimal_data = {
        'name': 'Minimal Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.create(minimal_data)
        
        # Verify stipend was created with minimal data
        stipend = Stipend.query.filter_by(name='Minimal Stipend').first()
        assert stipend is not None
        assert stipend.summary is None
        assert stipend.description is None

def test_update_stipend_with_empty_fields(test_data, db_session, app, admin_user):
    """Test updating stipend with empty optional fields"""
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    update_data = {
        'name': 'Updated Stipend',
        'summary': '',
        'description': '',
        'organization_id': stipend.organization_id
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.update(stipend.id, update_data)
        
        # Verify update
        updated_stipend = Stipend.query.get(stipend.id)
        assert updated_stipend.name == 'Updated Stipend'
        assert updated_stipend.summary is None
        assert updated_stipend.description is None

def test_stipend_service_rate_limiting(test_data, app):
    """Test rate limiting in stipend service"""
    service = StipendService()
    
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    # Make 11 requests (limit is 10 per minute)
    with pytest.raises(Exception) as exc_info:
        for i in range(11):
            service.create(test_data)
            
    assert "Rate limit exceeded" in str(exc_info.value)

def test_stipend_service_audit_logging(test_data, db_session, app, admin_user):
    """Test audit logging in stipend service"""
    from app.models.audit_log import AuditLog
    
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.create(test_data)
        
        # Verify audit log was created
        log = AuditLog.query.filter_by(object_type='Stipend').first()
        assert log is not None
        assert log.action == 'create'
        assert log.object_id == result.id

def test_create_stipend_with_invalid_organization(test_data, db_session, app):
    """Test creating stipend with invalid organization"""
    test_data['organization_id'] = 9999  # Non-existent organization
    
    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
        
    assert "Invalid organization" in str(exc_info.value)

def test_update_stipend_with_invalid_data(test_data, db_session, app):
    """Test updating stipend with invalid data"""
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    invalid_data = {
        'name': '',  # Invalid name
        'application_deadline': 'invalid-date'
    }

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.update(stipend.id, invalid_data)
        
    errors = exc_info.value.args[0]
    assert 'name' in errors
    assert 'application_deadline' in errors

def test_delete_stipend_with_dependencies(test_data, db_session, app):
    """Test deleting stipend with dependent records"""
    from app.models.tag import Tag
    
    # Create stipend with tags
    stipend = Stipend(**test_data)
    tag = Tag(name="Test Tag")
    stipend.tags.append(tag)
    db.session.add(stipend)
    db.session.commit()

    service = StipendService()
    
    # Should still be able to delete
    result = service.delete(stipend.id)
    assert result is True
    
    # Verify deletion
    assert Stipend.query.get(stipend.id) is None
    assert Tag.query.get(tag.id) is not None  # Tags should remain

def test_create_stipend_with_duplicate_name(test_data, db_session, app):
    """Test creating stipend with duplicate name"""
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    # Create initial stipend
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
        
    assert "already exists" in str(exc_info.value)

def test_create_stipend_with_past_deadline(test_data, db_session, app):
    """Test creating stipend with past deadline"""
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id
    test_data['application_deadline'] = '2020-01-01 00:00:00'  # Past date

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
        
    assert "must be in the future" in str(exc_info.value)

def test_update_stipend_with_invalid_tags(test_data, db_session, app):
    """Test updating stipend with invalid tags"""
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    invalid_data = {
        'tags': [9999]  # Non-existent tag
    }

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.update(stipend.id, invalid_data)
        
    assert "Invalid tags" in str(exc_info.value)
