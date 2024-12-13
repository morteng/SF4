import pytest
from flask import url_for
from app.models.stipend import Stipend
from tests.conftest import extract_csrf_token

@pytest.fixture(scope='function')
def stipend_data():
    """Provide test data for stipends."""
    return {
        'name': 'Test Stipend',
        'summary': 'Test summary content.',
        'description': 'A test stipend for testing purposes.',
        'homepage_url': 'http://example.com',
        'application_procedure': 'Follow the steps outlined on the website.',
        'eligibility_criteria': 'Must be enrolled in a degree program.',
        'application_deadline': '2024-12-31 23:59:59',
        'open_for_applications': True
    }

@pytest.fixture(scope='function')
def test_stipend(db_session, stipend_data):
    """Provide a test stipend for use in tests."""
    from datetime import datetime

    stipend = Stipend(
        name=stipend_data['name'],
        summary=stipend_data['summary'],
        description=stipend_data['description'],
        homepage_url=stipend_data['homepage_url'],
        application_procedure=stipend_data['application_procedure'],
        eligibility_criteria=stipend_data['eligibility_criteria'],
        application_deadline=datetime.strptime(stipend_data['application_deadline'], '%Y-%m-%d %H:%M:%S'),
        open_for_applications=stipend_data['open_for_applications']
    )
    db_session.add(stipend)
    db_session.commit()
    yield stipend

    # Teardown: Attempt to delete the stipend and rollback if an error occurs
    try:
        db_session.delete(stipend)
        db_session.commit()
    except Exception as e:
        print(f"Failed to delete test stipend during teardown: {e}")
        db_session.rollback()

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
    assert any(
        stipend.name == stipend_data['name'] and
        stipend.summary == stipend_data['summary'] and
        stipend.description == stipend_data['description'] and
        stipend.homepage_url == stipend_data['homepage_url'] and
        stipend.application_procedure == stipend_data['application_procedure'] and
        stipend.eligibility_criteria == stipend_data['eligibility_criteria'] and
        stipend.open_for_applications == stipend_data['open_for_applications']
        for stipend in stipends
    )

def test_create_stipend_route_with_invalid_data(logged_in_admin, stipend_data):
    create_response = logged_in_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    invalid_data = {
        'name': '',  # Invalid name
        'summary': stipend_data['summary'],
        'description': stipend_data['description'],
        'homepage_url': stipend_data['homepage_url'],
        'application_procedure': stipend_data['application_procedure'],
        'eligibility_criteria': stipend_data['eligibility_criteria'],
        'application_deadline': 'invalid-date',  # Invalid date
        'open_for_applications': stipend_data['open_for_applications'],
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.stipend.create'), data=invalid_data, follow_redirects=True)

    assert response.status_code == 200
    stipends = Stipend.query.all()
    assert not any(stipend.name == '' for stipend in stipends)  # Ensure no stipend with an empty name was created

def test_update_stipend_route(logged_in_admin, test_stipend, db_session):
    update_response = logged_in_admin.get(url_for('admin.stipend.update', id=test_stipend.id))
    assert update_response.status_code == 200

    csrf_token = extract_csrf_token(update_response.data)
    updated_data = {
        'name': 'Updated Stipend Name',
        'summary': 'Updated summary content.',
        'description': test_stipend.description,
        'homepage_url': test_stipend.homepage_url,
        'application_procedure': test_stipend.application_procedure,
        'eligibility_criteria': test_stipend.eligibility_criteria,
        'application_deadline': test_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S'),
        'open_for_applications': False,
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data, follow_redirects=True)

    assert response.status_code == 200
    updated_stipend = db_session.get(Stipend, test_stipend.id)  # Use db_session.get to retrieve the stipend
    assert updated_stipend.name == 'Updated Stipend Name'
    assert updated_stipend.summary == 'Updated summary content.'
    assert updated_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == test_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S')
    assert not updated_stipend.open_for_applications

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
        
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=data)
        
        assert response.status_code == 200
        assert b"Failed to create stipend." in response.data  # Confirm error message is present

        stipends = Stipend.query.all()
        assert not any(stipend.name == data['name'] for stipend in stipends)  # Ensure no stipend was created

def test_update_stipend_with_database_error(logged_in_admin, test_stipend, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        update_response = logged_in_admin.get(url_for('admin.stipend.update', id=test_stipend.id))
        assert update_response.status_code == 200

        csrf_token = extract_csrf_token(update_response.data)
        updated_data = {
            'name': 'Updated Stipend Name',
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
        assert b"Failed to update stipend." in response.data  # Confirm error message is present

        updated_stipend = db_session.get(Stipend, test_stipend.id)  # Use db_session.get to retrieve the stipend
        assert updated_stipend.name != 'Updated Stipend Name'
