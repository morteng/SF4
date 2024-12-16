import pytest
from flask import url_for
from app.models.stipend import Stipend
from tests.conftest import extract_csrf_token
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
        'application_deadline': '2023-12-31 23:59:59',  # Keep as string
        'open_for_applications': True
    }

@pytest.fixture(scope='function')
def test_stipend(db_session, stipend_data):
    """Provide a test stipend."""
    stipend_data['application_deadline'] = datetime.strptime(stipend_data['application_deadline'], '%Y-%m-%d %H:%M:%S')  # Convert to datetime here
    stipend = Stipend(**stipend_data)
    db_session.add(stipend)
    db_session.commit()
    yield stipend
    db_session.delete(stipend)
    db_session.commit()

def test_create_stipend_route(logged_in_admin, stipend_data):
    create_response = logged_in_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    response = logged_in_admin.post(url_for('admin.stipend.create'), data={
        'name': stipend_data['name'],
        'summary': stipend_data['summary'],
        'description': stipend_data['description'],
        'homepage_url': stipend_data['homepage_url'],
        'application_procedure': stipend_data['application_procedure'],
        'eligibility_criteria': stipend_data['eligibility_criteria'],
        'application_deadline': stipend_data['application_deadline'].strftime('%Y-%m-%d %H:%M:%S'),
        'open_for_applications': stipend_data['open_for_applications'],
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    stipends = Stipend.query.all()
    assert any(stipend.name == stipend_data['name'] and stipend.summary == stipend_data['summary'] for stipend in stipends)
    # Assert the flash message
    assert FLASH_MESSAGES["CREATE_STIPEND_SUCCESS"].encode() in response.data

def test_create_stipend_route_with_invalid_application_deadline_format(logged_in_admin, stipend_data):
    create_response = logged_in_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    invalid_data = stipend_data.copy()
    invalid_data['application_deadline'] = '2023-13-32 99:99:99'
    response = logged_in_admin.post(url_for('admin.stipend.create'), data={
        'name': invalid_data['name'],
        'summary': invalid_data['summary'],
        'description': invalid_data['description'],
        'homepage_url': invalid_data['homepage_url'],
        'application_procedure': invalid_data['application_procedure'],
        'eligibility_criteria': invalid_data['eligibility_criteria'],
        'application_deadline': invalid_data['application_deadline'],
        'open_for_applications': invalid_data['open_for_applications'],
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    stipends = Stipend.query.all()
    assert not any(stipend.name == invalid_data['name'] for stipend in stipends)
    # Assert the flash message
    assert FLASH_MESSAGES["CREATE_STIPEND_ERROR"].encode() in response.data

def test_update_stipend_route(logged_in_admin, test_stipend, db_session):
    update_response = logged_in_admin.get(url_for('admin.stipend.update', id=test_stipend.id))
    assert update_response.status_code == 200

    csrf_token = extract_csrf_token(update_response.data)
    updated_data = {
        'name': 'Updated Stipend',
        'summary': test_stipend.summary,
        'description': test_stipend.description,
        'homepage_url': test_stipend.homepage_url,
        'application_procedure': test_stipend.application_procedure,
        'eligibility_criteria': test_stipend.eligibility_criteria,
        'application_deadline': test_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S'),
        'open_for_applications': test_stipend.open_for_applications,
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data, follow_redirects=True)

    assert response.status_code == 200
    updated_stipend = db_session.get(Stipend, test_stipend.id)
    assert updated_stipend.name == 'Updated Stipend'
    # Assert the flash message
    assert FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"].encode() in response.data

def test_update_stipend_route_with_invalid_id(logged_in_admin):
    update_response = logged_in_admin.get(url_for('admin.stipend.update', id=9999))
    assert update_response.status_code == 302
    assert url_for('admin.stipend.index', _external=False) == update_response.headers['Location']

def test_delete_stipend_route(logged_in_admin, test_stipend, db_session):
    # Perform the DELETE operation
    delete_response = logged_in_admin.post(url_for('admin.stipend.delete', id=test_stipend.id))
    assert delete_response.status_code == 302
    
    # Ensure the stipend is no longer in the session after deleting
    db_session.expire_all()
    updated_stipend = db_session.get(Stipend, test_stipend.id)
    assert updated_stipend is None
    # Assert the flash message
    assert FLASH_MESSAGES["DELETE_STIPEND_SUCCESS"].encode() in delete_response.data

def test_delete_stipend_route_with_invalid_id(logged_in_admin):
    delete_response = logged_in_admin.post(url_for('admin.stipend.delete', id=9999))
    assert delete_response.status_code == 302
    assert url_for('admin.stipend.index', _external=False) == delete_response.headers['Location']

def test_create_stipend_route_with_database_error(logged_in_admin, stipend_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        data = stipend_data

        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.stipend.create'), data={
            'name': data['name'],
            'summary': data['summary'],
            'description': data['description'],
            'homepage_url': data['homepage_url'],
            'application_procedure': data['application_procedure'],
            'eligibility_criteria': data['eligibility_criteria'],
            'application_deadline': data['application_deadline'].strftime('%Y-%m-%d %H:%M:%S'),
            'open_for_applications': data['open_for_applications'],
            'csrf_token': extract_csrf_token(logged_in_admin.get(url_for('admin.stipend.create')).data)
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["CREATE_STIPEND_ERROR"].encode() in response.data  # Confirm error message is present

        stipends = Stipend.query.all()
        assert not any(stipend.name == data['name'] for stipend in stipends)  # Ensure no stipend was created

def test_update_stipend_route_with_database_error(logged_in_admin, test_stipend, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': 'Updated Stipend',
            'summary': test_stipend.summary,
            'description': test_stipend.description,
            'homepage_url': test_stipend.homepage_url,
            'application_procedure': test_stipend.application_procedure,
            'eligibility_criteria': test_stipend.eligibility_criteria,
            'application_deadline': test_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'open_for_applications': test_stipend.open_for_applications
        }

        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data={
            'name': updated_data['name'],
            'summary': updated_data['summary'],
            'description': updated_data['description'],
            'homepage_url': updated_data['homepage_url'],
            'application_procedure': updated_data['application_procedure'],
            'eligibility_criteria': updated_data['eligibility_criteria'],
            'application_deadline': updated_data['application_deadline'],
            'open_for_applications': updated_data['open_for_applications'],
            'csrf_token': extract_csrf_token(logged_in_admin.get(url_for('admin.stipend.update', id=test_stipend.id)).data)
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["UPDATE_STIPEND_ERROR"].encode() in response.data  # Confirm error message is present

        updated_stipend = db_session.get(Stipend, test_stipend.id)
        assert updated_stipend.name != 'Updated Stipend'
