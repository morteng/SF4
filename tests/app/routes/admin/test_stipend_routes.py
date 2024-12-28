import pytest
import logging
from flask import url_for
from flask.testing import FlaskClient
from datetime import datetime, timedelta
from pytz import timezone
from app.models.stipend import Stipend
from app.models.organization import Organization
from app.models.tag import Tag
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.constants import FlashMessages, FlashCategory
from tests.conftest import extract_csrf_token
from tests.utils import AuthActions

logger = logging.getLogger(__name__)

@pytest.fixture
def authenticated_admin(client: FlaskClient, auth: AuthActions) -> FlaskClient:
    """Fixture to authenticate as an admin user."""
    auth.login()
    return client

@pytest.fixture(scope='function')
def stipend_data():
    return {
        'name': 'Test Stipend',
        'summary': 'This is a test stipend.',
        'description': 'Detailed description of the test stipend.',
        'homepage_url': 'http://example.com/stipend',
        'application_procedure': 'Apply online at example.com',
        'eligibility_criteria': 'Open to all students',
        'application_deadline': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S'),  # Future date
        'open_for_applications': True
    }

@pytest.fixture(scope='function')
def test_stipend(db_session, stipend_data):
    """Provide a test stipend."""
    stipend_data['application_deadline'] = datetime.strptime(stipend_data['application_deadline'], '%Y-%m-%d %H:%M:%S')  # Convert to datetime here
    organization = Organization(name='Test Org')
    db_session.add(organization)
    db_session.commit()
    stipend = Stipend(**stipend_data, organization_id=organization.id)
    db_session.add(stipend)
    db_session.commit()
    yield stipend
    db_session.delete(stipend)
    db_session.commit()

def test_create_stipend_route(authenticated_admin: FlaskClient, db_session) -> None:
    """Test that a stipend can be created successfully through the admin interface."""
    # Create organization and tags
    organization = Organization(name='Test Org')
    tag1 = Tag(name='Research', category='Academic')
    tag2 = Tag(name='Scholarship', category='Funding')
    db_session.add_all([organization, tag1, tag2])
    db_session.commit()
    
    # Get create page and extract CSRF token
    create_response = authenticated_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200
    csrf_token = extract_csrf_token(create_response.data)
    
    # Prepare form data
    form_data = {
        'name': 'Test Stipend',
        'summary': 'Test summary',
        'description': 'Test description',
        'homepage_url': 'http://example.com',
        'application_procedure': 'Apply online',
        'eligibility_criteria': 'Open to all',
        'application_deadline': (datetime.now(timezone.utc) + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
        'organization_id': str(organization.id),
        'tags': [str(tag1.id), str(tag2.id)],
        'open_for_applications': True,
        'csrf_token': csrf_token
    }
    
    # Submit form
    response = authenticated_admin.post(
        url_for('admin.stipend.create'), 
        data=form_data, 
        follow_redirects=True
    )
    
    # Verify response
    assert response.status_code == 200
    
    # Check database for created stipend
    created_stipend = Stipend.query.filter_by(name='Test Stipend').first()
    assert created_stipend is not None
    assert created_stipend.summary == 'Test summary'
    assert created_stipend.organization_id == organization.id
    assert len(created_stipend.tags) == 2
    
    # Verify audit log
    audit_log = AuditLog.query.filter_by(object_type='Stipend', object_id=created_stipend.id).first()
    assert audit_log is not None
    assert audit_log.action == 'create_stipend'
    
    # Verify notification
    notification = Notification.query.filter_by(related_object=created_stipend).first()
    assert notification is not None
    assert notification.type == 'STIPEND_CREATED'
    
    # Verify flash message
    assert FlashMessages.CREATE_STIPEND_SUCCESS.value.encode() in response.data
    
    # Verify flash message
    assert FlashMessages.CREATE_STIPEND_SUCCESS.value.encode() in response.data, "Success message not found"
    
    logger.info("Completed test_create_stipend_route")
    # Create organization first
    organization = Organization(name='Test Org')
    db_session.add(organization)
    db_session.commit()
    
    # Get create page and extract CSRF token
    create_response = authenticated_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200
    csrf_token = extract_csrf_token(create_response.data)
    
    # Prepare form data
    form_data = {
        'name': stipend_data['name'],
        'summary': stipend_data['summary'],
        'description': stipend_data['description'],
        'homepage_url': stipend_data['homepage_url'],
        'application_procedure': stipend_data['application_procedure'],
        'eligibility_criteria': stipend_data['eligibility_criteria'],
        'application_deadline': stipend_data['application_deadline'],  # Use future date from fixture
        'organization_id': str(organization.id),  # Converted to string
        'open_for_applications': True,  # Changed to boolean
        'csrf_token': csrf_token
    }
    
    # Submit form
    response = authenticated_admin.post(url_for('admin.stipend.create'), 
                                  data=form_data, 
                                  follow_redirects=True)
    
    # Verify response
    assert response.status_code == 200
    
    # Check database for created stipend
    created_stipend = Stipend.query.filter_by(name=stipend_data['name']).first()
    assert created_stipend is not None
    assert created_stipend.summary == stipend_data['summary']
    assert created_stipend.organization_id == organization.id
    
    # Verify flash message
    assert FlashMessages.CREATE_STIPEND_SUCCESS.value.encode() in response.data

@pytest.mark.parametrize("invalid_date, expected_message", [
    ("2023-13-32 99:99:99", "Invalid date format"),
    ("2023-02-30 12:00:00", "Invalid date"),  # February 30th
    ("2023-04-31 12:00:00", "Invalid date"),  # April 31st
    ("2023-00-01 12:00:00", "Invalid date"),  # Month 00
    ("2023-01-00 12:00:00", "Invalid date"),  # Day 00
])
def test_create_stipend_with_invalid_dates(
    authenticated_admin: FlaskClient, 
    stipend_data: dict, 
    db_session, 
    invalid_date: str,
    expected_message: str
) -> None:
    """Test validation of invalid application deadline dates."""
    logger.info(f"Starting test_create_stipend_with_invalid_dates: {invalid_date}")
    
    # Create organization
    organization = Organization(name='Test Org Invalid Date')
    db_session.add(organization)
    db_session.commit()
    
    # Get create page and extract CSRF token
    create_response = authenticated_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200, "Failed to load create stipend page"
    csrf_token = extract_csrf_token(create_response.data)
    
    # Prepare invalid data
    invalid_data = {
        'name': stipend_data['name'],
        'summary': stipend_data['summary'],
        'description': stipend_data['description'],
        'homepage_url': stipend_data['homepage_url'],
        'application_procedure': stipend_data['application_procedure'],
        'eligibility_criteria': stipend_data['eligibility_criteria'],
        'application_deadline': invalid_date,
        'organization_id': str(organization.id),
        'open_for_applications': True,
        'csrf_token': csrf_token
    }
    
    # Submit form
    response = authenticated_admin.post(
        url_for('admin.stipend.create'), 
        data=invalid_data,
        follow_redirects=True
    )
    
    # Verify response
    assert response.status_code == 400, "Expected 400 status for invalid date"
    
    # Verify no stipend was created
    stipends = Stipend.query.all()
    assert not any(stipend.name == invalid_data['name'] for stipend in stipends), "Stipend was incorrectly created"
    
    # Check for error message
    assert expected_message.encode() in response.data, f"Expected error message for {invalid_date} not found"
    
    logger.info(f"Completed test_create_stipend_with_invalid_dates: {invalid_date}")
    create_response = authenticated_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    
    # Create an organization for the test
    organization = Organization(name='Test Org Invalid Deadline')
    db_session.add(organization)
    db_session.commit()  # Commit the organization to the database
    
    invalid_data = {
        'name': stipend_data['name'],
        'summary': stipend_data['summary'],
        'description': stipend_data['description'],
        'homepage_url': stipend_data['homepage_url'],
        'application_procedure': stipend_data['application_procedure'],
        'eligibility_criteria': stipend_data['eligibility_criteria'],
        'application_deadline': '2023-13-32 99:99:99',  # Invalid date format
        'organization_id': str(organization.id),  # Converted to string
        'open_for_applications': True,  # Changed to boolean
        'csrf_token': csrf_token
    }
    
    response = authenticated_admin.post(url_for('admin.stipend.create'), 
                                  data=invalid_data,
                                  follow_redirects=True)
 
    assert response.status_code == 400
    stipends = Stipend.query.all()
    assert not any(stipend.name == invalid_data['name'] for stipend in stipends)
    # Check for either the flash message or form validation error
    # Check for any date validation error message
    assert (b'Invalid date' in response.data or 
            b'Invalid datetime' in response.data or
            b'date format' in response.data)

def test_update_stipend_route(authenticated_admin: FlaskClient, test_stipend: Stipend, db_session) -> None:
    """Test that a stipend can be updated successfully through the admin interface."""
    logger.info("Starting test_update_stipend_route")
    
    # Get the edit page to extract CSRF token
    update_response = authenticated_admin.get(url_for('admin.stipend.edit', id=test_stipend.id))
    assert update_response.status_code == 200, "Failed to load edit stipend page"
    csrf_token = extract_csrf_token(update_response.data)

    # Prepare updated data
    updated_data = {
        'name': 'Updated Stipend',
        'summary': test_stipend.summary,
        'description': test_stipend.description,
        'homepage_url': test_stipend.homepage_url,
        'application_procedure': test_stipend.application_procedure,
        'eligibility_criteria': test_stipend.eligibility_criteria,
        'application_deadline': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S'),
        'organization_id': test_stipend.organization_id,
        'open_for_applications': True,
        'csrf_token': csrf_token
    }

    # Test HTMX case
    htmx_response = authenticated_admin.post(
        url_for('admin.stipend.edit', id=test_stipend.id),
        data=updated_data,
        headers={'HX-Request': 'true'}
    )
    assert htmx_response.status_code == 200, "HTMX update failed"
    assert b'<tr hx-target="this" hx-swap="outerHTML">' in htmx_response.data, "HTMX response format incorrect"

    # Test non-HTMX case
    non_htmx_response = authenticated_admin.post(
        url_for('admin.stipend.edit', id=test_stipend.id),
        data=updated_data
    )
    assert non_htmx_response.status_code == 302, "Non-HTMX update failed"
    assert non_htmx_response.location.startswith('/admin/stipends/'), "Incorrect redirect location"

    # Follow the redirect for non-HTMX case
    final_response = authenticated_admin.get(non_htmx_response.location)
    assert final_response.status_code == 200, "Failed to load redirect page"

    # Verify the stipend was updated
    updated_stipend = Stipend.query.filter_by(id=test_stipend.id).first()
    assert updated_stipend is not None, "Stipend not found in database"
    assert updated_stipend.name == 'Updated Stipend', "Stipend name not updated"

    # Verify the success flash message
    assert FlashMessages.UPDATE_STIPEND_SUCCESS.value.encode() in final_response.data, "Success message not found"
    

def test_delete_stipend_route(authenticated_admin: FlaskClient, test_stipend: Stipend, db_session) -> None:
    """Test that a stipend can be deleted successfully through the admin interface."""
    logger.info("Starting test_delete_stipend_route")
    
    response = authenticated_admin.post(
        url_for('admin.stipend.delete', id=test_stipend.id), 
        follow_redirects=True
    )
    assert response.status_code == 200, "Failed to delete stipend"
    
    # Verify the stipend was deleted
    deleted_stipend = Stipend.query.filter_by(id=test_stipend.id).first()
    assert deleted_stipend is None, "Stipend was not deleted from database"
    
    # Verify the success flash message
    assert FlashMessages.DELETE_STIPEND_SUCCESS.value.encode() in response.data, "Success message not found"
    

def test_index_stipend_route(authenticated_admin: FlaskClient, test_stipend: Stipend) -> None:
    """Test that the stipend index page displays stipends correctly."""
    logger.info("Starting test_index_stipend_route")
    
    response = authenticated_admin.get(url_for('admin.stipend.index'))
    assert response.status_code == 200, "Failed to load stipend index page"
    assert test_stipend.name.encode() in response.data, "Stipend not found in index page"
    

def test_paginate_stipend_route(authenticated_admin: FlaskClient, test_stipend: Stipend) -> None:
    """Test that stipend pagination works correctly."""
    logger.info("Starting test_paginate_stipend_route")
    
    response = authenticated_admin.get(url_for('admin.stipend.paginate', page=1))
    assert response.status_code == 200, "Failed to load paginated stipends"
    assert test_stipend.name.encode() in response.data, "Stipend not found in paginated results"
    

def test_create_stipend_route_htmx(logged_in_admin, stipend_data, db_session):
    # Ensure an organization exists for the test
    organization = Organization(name='Test Org HTMX')
    db_session.add(organization)
    db_session.commit()
    stipend_data['organization_id'] = organization.id

    create_response = logged_in_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    response = logged_in_admin.post(url_for('admin.stipend.create'), headers={'HX-Request': 'true'}, data={
        'name': stipend_data['name'],
        'summary': stipend_data['summary'],
        'description': stipend_data['description'],
        'homepage_url': stipend_data['homepage_url'],
        'application_procedure': stipend_data['application_procedure'],
        'eligibility_criteria': stipend_data['eligibility_criteria'],
        'application_deadline': stipend_data['application_deadline'],  # Edited Line
        'organization_id': stipend_data['organization_id'],
        'open_for_applications': True,  # Changed to boolean
       'csrf_token': csrf_token
   }, follow_redirects=True)
 
    assert response.status_code == 200
    # Verify either the row was rendered or we got an error message
    assert (b'<tr id="stipend-row-' in response.data or 
            b'Error rendering new row' in response.data)
    # Verify the stipend was created
    created_stipend = Stipend.query.filter_by(name=stipend_data['name']).first()
    assert created_stipend is not None
    assert created_stipend.summary == stipend_data['summary']
    # Verify the flash message for successful creation
    assert FlashMessages.CREATE_STIPEND_SUCCESS.value.encode() in response.data

def test_create_stipend_route_with_invalid_application_deadline_format_htmx(logged_in_admin, stipend_data, db_session):
    # Create an organization for the test
    organization = Organization(name='Test Org Invalid Deadline HTMX')
    db_session.add(organization)
    db_session.commit()

    create_response = logged_in_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    invalid_data = stipend_data.copy()
    invalid_data['application_deadline'] = '2023-13-32 99:99:99'
    response = logged_in_admin.post(url_for('admin.stipend.create'), headers={'HX-Request': 'true'}, data={
        'name': invalid_data['name'],
        'summary': invalid_data['summary'],
        'description': invalid_data['description'],
        'homepage_url': invalid_data['homepage_url'],
        'application_procedure': invalid_data['application_procedure'],
        'eligibility_criteria': invalid_data['eligibility_criteria'],
        'application_deadline': invalid_data['application_deadline'],
        'organization_id': organization.id,
        'open_for_applications': invalid_data['open_for_applications'],
       'csrf_token': csrf_token
   }, follow_redirects=True)
 
    assert response.status_code == 400
    stipends = Stipend.query.all()
    assert not any(stipend.name == invalid_data['name'] for stipend in stipends)
    # Assert the flash message
    assert b'Invalid date format. Please use YYYY-MM-DD HH:MM:SS' in response.data

def test_create_stipend_with_invalid_form_data_htmx(logged_in_admin, stipend_data, db_session):
    # Create organization first
    organization = Organization(name='Test Org Invalid Form Data HTMX')
    db_session.add(organization)
    db_session.commit()
    
    # Get the form page to extract CSRF token
    create_response = logged_in_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200
    csrf_token = extract_csrf_token(create_response.data)
    
    # Prepare form data with empty 'name' and include CSRF token
    invalid_data = {
        'name': '',  # Intentionally invalid
        'summary': stipend_data['summary'],
        'description': stipend_data['description'],
        'homepage_url': stipend_data['homepage_url'],
        'application_procedure': stipend_data['application_procedure'],
        'eligibility_criteria': stipend_data['eligibility_criteria'],
        'application_deadline': stipend_data['application_deadline'],
        'organization_id': organization.id,  # Use the created organization's ID
        'open_for_applications': stipend_data['open_for_applications'],
        'csrf_token': csrf_token  # Include CSRF token
    }
    
    # Submit form with HTMX headers
    response = logged_in_admin.post(
        url_for('admin.stipend.create'),
        data=invalid_data,
        headers={'HX-Request': 'true'},
       follow_redirects=True
   )
    
    assert response.status_code == 400
    # Check if validation error is present
    assert b'Name: Name is required.' in response.data, "Validation error not found in response"
    # Verify no stipend was created
    stipends = db_session.query(Stipend).all()
    assert not any(stipend.name == invalid_data['name'] for stipend in stipends)


def test_update_stipend_route_htmx(logged_in_admin, test_stipend, db_session):
    update_response = logged_in_admin.get(url_for('admin.stipend.edit', id=test_stipend.id))
    assert update_response.status_code == 200

    csrf_token = extract_csrf_token(update_response.data)
    updated_data = {
        'name': 'Updated Stipend',
        'summary': test_stipend.summary,
        'description': test_stipend.description,
        'homepage_url': test_stipend.homepage_url,
        'application_procedure': test_stipend.application_procedure,
        'eligibility_criteria': test_stipend.eligibility_criteria,
        'application_deadline': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'organization_id': test_stipend.organization_id,
        'open_for_applications': test_stipend.open_for_applications,
        'csrf_token': csrf_token
   }
    response = logged_in_admin.post(
        url_for('admin.stipend.edit', id=test_stipend.id),
        headers={'HX-Request': 'true'},
        data=updated_data
    )
    
    assert response.status_code == 200
    updated_stipend = Stipend.query.filter_by(id=test_stipend.id).first()
    assert updated_stipend.name == 'Updated Stipend'
    # Assert the flash message
    assert FlashMessages.UPDATE_STIPEND_SUCCESS.value.encode() in response.data
