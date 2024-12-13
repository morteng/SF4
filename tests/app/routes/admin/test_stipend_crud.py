import pytest
from flask import url_for
from app.models.stipend import Stipend
from tests.conftest import extract_csrf_token

@pytest.fixture(scope='function')
def stipend_data():
    """Provide test data for stipends."""
    return {
        'name': 'Test Stipend',
        'description': 'A test stipend for testing purposes.',
        'amount': 1000
    }

@pytest.fixture(scope='function')
def test_stipend(db_session, stipend_data):
    """Provide a test stipend for use in tests."""
    stipend = Stipend(
        name=stipend_data['name'],
        description=stipend_data['description'],
        amount=stipend_data['amount']
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
        'description': stipend_data['description'],
        'amount': stipend_data['amount'],
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    stipends = Stipend.query.all()
    assert any(stipend.name == stipend_data['name'] and stipend.description == stipend_data['description'] for stipend in stipends)

def test_create_stipend_route_with_invalid_data(logged_in_admin, stipend_data):
    create_response = logged_in_admin.get(url_for('admin.stipend.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    invalid_data = {
        'name': '',  # Invalid name
        'description': stipend_data['description'],
        'amount': stipend_data['amount'],
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
        'description': test_stipend.description,
        'amount': test_stipend.amount,
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data, follow_redirects=True)

    assert response.status_code == 200
    updated_stipend = db_session.get(Stipend, test_stipend.id)  # Use db_session.get to retrieve the stipend
    assert updated_stipend.name == 'Updated Stipend Name'

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
            'description': test_stipend.description,
            'amount': test_stipend.amount,
            'csrf_token': csrf_token
        }
        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"Failed to update stipend." in response.data  # Confirm error message is present

        updated_stipend = db_session.get(Stipend, test_stipend.id)  # Use db_session.get to retrieve the stipend
        assert updated_stipend.name != 'Updated Stipend Name'
