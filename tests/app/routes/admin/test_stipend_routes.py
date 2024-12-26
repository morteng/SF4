import pytest
from flask import url_for
from app.models.stipend import Stipend
from tests.conftest import extract_csrf_token
from app.models.organization import Organization
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR
from datetime import datetime

@pytest.fixture(scope='function')
def stipend_data():
    return {
        'name': 'Test Stipend',
        'summary': 'This is a test stipend.',
        'description': 'Detailed description of the test stipend.',
        'homepage_url': 'http://example.com/stipend',
        'application_procedure': 'Apply online at example.com',
        'eligibility_criteria': 'Open to all students',
        'application_deadline': '2023-12-31 23:59:59',  # Use consistent format
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

def test_create_stipend_route(logged_in_admin, stipend_data, db_session):
    print("\n[DEBUG] Starting test_create_stipend_route")
    print(f"[DEBUG] Initial stipend_data: {stipend_data}")
    
    # Create and commit organization first
    organization = Organization(name='Test Org')
    db_session.add(organization)
    db_session.commit()
    print(f"[DEBUG] Created organization with ID: {organization.id}")
    
    # Update stipend data with organization ID
    stipend_data['organization_id'] = organization.id
    print(f"[DEBUG] Updated stipend_data with organization_id: {stipend_data}")
    
    # Get create page and extract CSRF token
    create_response = logged_in_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200
    csrf_token = extract_csrf_token(create_response.data)
    print(f"[DEBUG] Extracted CSRF token: {csrf_token}")
    
    # Prepare form data
    form_data = {
        'name': stipend_data['name'],
        'summary': stipend_data['summary'],
        'description': stipend_data['description'],
        'homepage_url': stipend_data['homepage_url'],
        'application_procedure': stipend_data['application_procedure'],
        'eligibility_criteria': stipend_data['eligibility_criteria'],
        'application_deadline': stipend_data['application_deadline'],
        'organization_id': organization.id,
        'open_for_applications': stipend_data['open_for_applications'],
        'csrf_token': csrf_token
    }
    print(f"[DEBUG] Prepared form_data: {form_data}")
    
    # Submit form
    response = logged_in_admin.post(url_for('admin.stipend.create'), 
                                  data=form_data, 
                                  follow_redirects=True)
    print(f"[DEBUG] Response status code: {response.status_code}")
    print(f"[DEBUG] Response data: {response.data.decode('utf-8')}")
    
    # Verify response
    assert response.status_code == 200
    
    # Check database for created stipend
    created_stipend = Stipend.query.filter_by(name=stipend_data['name']).first()
    print(f"[DEBUG] Created stipend: {created_stipend}")
    assert created_stipend is not None, "Stipend was not created"
    assert created_stipend.summary == stipend_data['summary'], "Stipend summary does not match"
    assert created_stipend.organization_id == organization.id, "Stipend not associated with correct organization"
    
    # Verify flash message
    assert FLASH_MESSAGES["CREATE_STIPEND_SUCCESS"].encode() in response.data, "Success flash message not found"
    print("[DEBUG] Test completed successfully")

def test_create_stipend_route_with_invalid_application_deadline_format(logged_in_admin, stipend_data, db_session):
    create_response = logged_in_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    
    # Create an organization for the test
    organization = Organization(name='Test Org Invalid Deadline')
    db_session.add(organization)
    db_session.commit()  # Commit the organization to the database
    
    invalid_data = stipend_data.copy()
    invalid_data['organization_id'] = organization.id
    invalid_data['application_deadline'] = '2023-13-32 99:99:99'
    response = logged_in_admin.post(url_for('admin.stipend.create'), data={
        'name': invalid_data['name'],
        'summary': invalid_data['summary'],
        'description': invalid_data['description'],
        'homepage_url': invalid_data['homepage_url'],
        'application_procedure': invalid_data['application_procedure'],
        'eligibility_criteria': invalid_data['eligibility_criteria'],
        'application_deadline': invalid_data['application_deadline'],
        'organization_id': organization.id,  # Use the ID of the created organization
        'open_for_applications': invalid_data['open_for_applications'],
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    stipends = Stipend.query.all()
    assert not any(stipend.name == invalid_data['name'] for stipend in stipends)
    # Assert the flash message
    assert FLASH_MESSAGES["INVALID_DATE_FORMAT"].encode() in response.data

def test_update_stipend_route(logged_in_admin, test_stipend, db_session):
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
        'application_deadline': test_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') if isinstance(test_stipend.application_deadline, datetime) else test_stipend.application_deadline,  # Changed this line
        'organization_id': test_stipend.organization_id,
        'open_for_applications': test_stipend.open_for_applications,
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.stipend.edit', id=test_stipend.id), data=updated_data, follow_redirects=True)

    assert response.status_code == 200
    updated_stipend = Stipend.query.filter_by(id=test_stipend.id).first()
    assert updated_stipend.name == 'Updated Stipend'
    # Assert the flash message
    assert FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"].encode() in response.data

def test_delete_stipend_route(logged_in_admin, test_stipend, db_session):
    response = logged_in_admin.post(url_for('admin.stipend.delete', id=test_stipend.id), follow_redirects=True)
    assert response.status_code == 200
    deleted_stipend = Stipend.query.filter_by(id=test_stipend.id).first()
    assert deleted_stipend is None
    # Assert the flash message
    assert FLASH_MESSAGES["DELETE_STIPEND_SUCCESS"].encode() in response.data

def test_index_stipend_route(logged_in_admin, test_stipend):
    response = logged_in_admin.get(url_for('admin.stipend.index'))
    assert response.status_code == 200
    assert test_stipend.name.encode() in response.data

def test_paginate_stipend_route(logged_in_admin, test_stipend):
    response = logged_in_admin.get(url_for('admin.stipend.paginate', page=1))
    assert response.status_code == 200
    assert test_stipend.name.encode() in response.data

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
        'open_for_applications': stipend_data['open_for_applications'],
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'<tr hx-target="this" hx-swap="outerHTML">' in response.data
    stipends = Stipend.query.all()
    assert any(stipend.name == stipend_data['name'] and stipend.summary == stipend_data['summary'] for stipend in stipends)
    # Assert the flash message
    assert FLASH_MESSAGES["CREATE_STIPEND_SUCCESS"].encode() in response.data

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

    assert response.status_code == 200
    stipends = Stipend.query.all()
    assert not any(stipend.name == invalid_data['name'] for stipend in stipends)
    # Assert the flash message
    assert FLASH_MESSAGES["INVALID_DATE_FORMAT"].encode() in response.data

def test_create_stipend_with_invalid_form_data_htmx(logged_in_admin, stipend_data, db_session):
    """Test HTMX form submission with invalid data (empty name field)"""
    # Create organization first
    organization = Organization(name='Test Org')
    db_session.add(organization)
    db_session.commit()
    
    # Get CSRF token
    create_response = logged_in_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200
    csrf_token = extract_csrf_token(create_response.data)
    
    # Prepare invalid form data
    invalid_data = {
        'name': '',  # Intentionally invalid
        'summary': stipend_data['summary'],
        'description': stipend_data['description'],
        'homepage_url': stipend_data['homepage_url'],
        'application_procedure': stipend_data['application_procedure'],
        'eligibility_criteria': stipend_data['eligibility_criteria'],
        'application_deadline': stipend_data['application_deadline'],
        'organization_id': organization.id,
        'open_for_applications': stipend_data['open_for_applications'],
        'csrf_token': csrf_token
    }
    
    # Submit form with HTMX headers
    response = logged_in_admin.post(
        url_for('admin.stipend.create'),
        data=invalid_data,
        headers={'HX-Request': 'true'},
        follow_redirects=True
    )

    # Verify response
    assert response.status_code == 200
    
    # Check for validation error in response
    assert b'This field is required.' in response.data, \
        "Expected validation error not found in response"
    
    # Verify no stipend was created in database
    stipend_count = db_session.query(Stipend).filter_by(organization_id=organization.id).count()
    assert stipend_count == 0, \
        "Stipend was created despite invalid form data"
    
    # Verify form is re-rendered with error
    assert b'form' in response.data.lower(), \
        "Expected form to be re-rendered with validation error"


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
        'application_deadline': test_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') if isinstance(test_stipend.application_deadline, datetime) else test_stipend.application_deadline,  # Changed this line
        'organization_id': test_stipend.organization_id,
        'open_for_applications': test_stipend.open_for_applications,
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.stipend.edit', id=test_stipend.id), headers={'HX-Request': 'true'}, data=updated_data, follow_redirects=True)

    assert response.status_code == 200
    updated_stipend = Stipend.query.filter_by(id=test_stipend.id).first()
    assert updated_stipend.name == 'Updated Stipend'
    # Assert the flash message
    assert FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"].encode() in response.data
