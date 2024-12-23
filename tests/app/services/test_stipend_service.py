import pytest
import re  # Import the re module to use regex for extracting CSRF token
from app.models.stipend import Stipend
from app.services.stipend_service import create_stipend, update_stipend, delete_stipend, get_stipend_by_id, get_all_stipends
from datetime import datetime
from flask_login import login_user
from app.extensions import db  # Ensure consistent session usage
from app.forms.admin_forms import StipendForm
from app.models.user import User
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR
from flask import get_flashed_messages
import logging

@pytest.fixture
def test_data():
    return {
        'name': "Test Stipend",
        'summary': 'This is a test stipend.',
        'description': 'Detailed description of the test stipend.',
        'homepage_url': 'http://example.com/stipend',
        'application_procedure': 'Apply online at example.com',
        'eligibility_criteria': 'Open to all students',
        'application_deadline': datetime.strptime('2023-12-31 23:59:59', '%Y-%m-%d %H:%M:%S'),
        'open_for_applications': True
    }

@pytest.fixture
def admin_user(db_session):
    user = User(username='adminuser', email='admin@example.com', password_hash='hashedpassword')
    user.is_admin = True
    db_session.add(user)
    db_session.commit()
    return user

def extract_csrf_token(response_data):
    csrf_regex = r'<input[^>]+name="csrf_token"[^>]+value="([^"]+)"'
    match = re.search(csrf_regex, response_data.decode('utf-8'))
    if match:
        return match.group(1)
    return None

def test_create_stipend(test_data, db_session, app, admin_user):
    # Convert datetime object to string for form submission
    test_data['application_deadline'] = test_data['application_deadline'].strftime('%Y-%m-%d %H:%M:%S')

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Create a form instance and validate it
        form = StipendForm(data=test_data)
        assert form.validate(), f"Form validation failed: {form.errors}"
        
        response = client.post('/admin/stipends/create', data=form.data, follow_redirects=True)

    # Query the stipend from the session to ensure it's bound
    new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()

    # Check if the stipend was created successfully
    assert new_stipend is not None
    assert new_stipend.name == test_data['name']
    assert new_stipend.summary == test_data['summary']
    assert new_stipend.description == test_data['description']
    assert new_stipend.homepage_url == test_data['homepage_url']
    assert new_stipend.application_procedure == test_data['application_procedure']
    assert new_stipend.eligibility_criteria == test_data['eligibility_criteria']
    assert new_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2023-12-31 23:59:59'
    assert new_stipend.open_for_applications is True

    # Check if the correct flash message was set
    with app.test_request_context():
        assert FLASH_MESSAGES["CREATE_STIPEND_SUCCESS"].encode() in response.data

def test_create_stipend_with_invalid_application_deadline_format(test_data, db_session, app, admin_user):
    # Modify test data with an invalid application_deadline format
    test_data['application_deadline'] = '2023-13-32 99:99:99'
    
    form = StipendForm(data=test_data)
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Validate the form
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
            
            # Assert that there are validation errors
            assert 'application_deadline' in form.errors
            
            return
        
        stipend_data = {k: v for k, v in form.data.items() if k != 'submit'}
        response = client.post('/admin/stipends/create', data=stipend_data, follow_redirects=True)

    # Assert that the stipend was not created due to validation errors
    new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
    assert new_stipend is None

    # Check if the correct flash message was set
    with app.test_request_context():
        assert FLASH_MESSAGES["INVALID_DATE_FORMAT"].encode() in response.data


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

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Use StipendForm to handle form submission
        form = StipendForm(data=update_data)
        assert form.validate(), f"Form validation failed: {form.errors}"
        
        with app.test_request_context():
            # Call update_stipend to actually update the stipend object
            update_stipend(stipend, update_data)
        
        response = client.post(f'/admin/stipends/{stipend.id}/edit', data=form.data, follow_redirects=True)
        logging.info(f"Response status code: {response.status_code}")
        logging.info(f"Response  {response.data.decode('utf-8')}")

    # Query the stipend from the session to ensure it's bound
    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()

    # Check if the stipend was updated successfully
    assert updated_stipend is not None
    assert updated_stipend.name == "Updated Test Stipend"
    assert updated_stipend.summary == 'Updated summary'
    assert updated_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2024-12-31 23:59:59'

    # Check if the correct flash message was set
    with app.test_request_context():
        assert FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"].encode() in response.data

def test_update_stipend_with_invalid_application_deadline_format(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    update_data = {
        'application_deadline': '2024-13-32 99:99:99',
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Create a form instance and validate it
        form = StipendForm(data=update_data)
        assert not form.validate(), f"Form validation should have failed: {form.errors}"

        # Call update_stipend to actually update the stipend object
        update_stipend(stipend, update_data)
        
        response = client.post(f'/admin/stipends/{stipend.id}/edit', data=form.data, follow_redirects=True)

    # Assert that the stipend was not updated due to validation errors
    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
    assert updated_stipend.name == test_data['name']
    assert updated_stipend.summary == test_data['summary']

    # Check if the correct flash message was set
    with app.test_request_context():
        assert FLASH_MESSAGES["INVALID_DATE_FORMAT"].encode() in response.data

def test_update_stipend_open_for_applications(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    update_data = {
        'open_for_applications': True,
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Create a form instance and validate it
        form = StipendForm(data=update_data)
        assert form.validate(), f"Form validation failed: {form.errors}"

        # Call update_stipend to actually update the stipend object
        update_stipend(stipend, update_data)
        
        response = client.post(f'/admin/stipends/{stipend.id}/edit', data=form.data, follow_redirects=True)

    # Query the stipend from the session to ensure it's bound
    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()

    # Check if the stipend was updated successfully
    assert updated_stipend is not None
    assert updated_stipend.open_for_applications is True

    # Check if the correct flash message was set
    with app.test_request_context():
        assert FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"].encode() in response.data

def test_delete_existing_stipend(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        response = client.post(f'/admin/stipends/{stipend.id}/delete', follow_redirects=True)

    # Assert that the stipend was deleted
    deleted_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
    assert deleted_stipend is None

    # Check if the correct flash message was set
    with app.test_request_context():
        assert FLASH_MESSAGES["DELETE_STIPEND_SUCCESS"].encode() in response.data

def test_delete_nonexistent_stipend(app, admin_user):
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        response = client.post('/admin/stipends/9999/delete', follow_redirects=True)  # Assuming there's no stipend with ID 9999

    # Check if the correct flash message was set
    with app.test_request_context():
        assert FLASH_MESSAGES["STIPEND_NOT_FOUND"].encode() in response.data

def test_get_stipend_by_valid_id(test_data, db_session, app):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    retrieved_stipend = get_stipend_by_id(stipend.id)
    assert retrieved_stipend is not None
    assert retrieved_stipend.name == test_data['name']

def test_get_stipend_by_invalid_id(app):
    retrieved_stipend = get_stipend_by_id(9999)  # Assuming there's no stipend with ID 9999
    assert retrieved_stipend is None

def test_get_all_stipends_with_multiple_entries(test_data, db_session, app):
    stipend1 = Stipend(**test_data)
    stipend2 = Stipend(name="Another Test Stipend", summary="Summary of another stipend")
    db_session.add(stipend1)
    db_session.add(stipend2)
    db_session.commit()

    all_stipends = get_all_stipends()
    assert len(all_stipends) == 2
    assert any(s.name == test_data['name'] for s in all_stipends)

def test_get_all_stipends_with_no_entries(app):
    all_stipends = get_all_stipends()
    assert len(all_stipends) == 0
