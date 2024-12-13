import pytest
from flask import url_for, get_flashed_messages
from app.models.stipend import Stipend
from tests.conftest import extract_csrf_token
from app.forms.admin_forms import StipendForm  # Added this line

@pytest.fixture(scope='function')
def stipend_data():
    return {
        'name': 'Test Stipend',
        'description': 'A test stipend for testing purposes.',
        'amount': 1000,
        'currency': 'USD'
    }

@pytest.fixture(scope='function')
def test_stipend(db_session, stipend_data):
    stipend = Stipend(**stipend_data)
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
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.stipend.create'))
        csrf_token = extract_csrf_token(response.data)

        response = logged_in_admin.post(url_for('admin.stipend.create'), data={
            'name': stipend_data['name'],
            'description': stipend_data['description'],
            'amount': stipend_data['amount'],
            'currency': stipend_data['currency'],
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200
        new_stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert new_stipend is not None

def test_create_stipend_route_with_invalid_data(logged_in_admin, stipend_data):
    with logged_in_admin.application.app_context():
        data = stipend_data
        
        # Intentionally make the name field invalid
        data['name'] = ''
        
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=data)
        
        assert response.status_code == 200

        form = StipendForm(data=data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
            
        # Check that the stipend was not created
        new_stipend = db_session.query(Stipend).filter_by(name=data['name']).first()
        assert new_stipend is None

def test_delete_stipend_route(logged_in_admin, test_stipend, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.stipend.delete', id=test_stipend.id))
        
        assert response.status_code == 302
        flash_message = list(filter(lambda x: 'deleted' in x, get_flashed_messages()))
        assert len(flash_message) > 0

        # Ensure the stipend is no longer in the session after deleting
        db_session.expire_all()
        updated_stipend = db_session.get(Stipend, test_stipend.id)
        assert updated_stipend is None

def test_delete_nonexistent_stipend_route(logged_in_admin):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.stipend.delete', id=9999))
        
        assert response.status_code == 302
        flash_message = list(filter(lambda x: 'not found' in x, get_flashed_messages()))
        assert len(flash_message) > 0

def test_update_stipend_route(logged_in_admin, test_stipend, db_session):
    with logged_in_admin.application.app_context():
        update_response = logged_in_admin.get(url_for('admin.stipend.update', id=test_stipend.id))
        assert update_response.status_code == 200

        csrf_token = extract_csrf_token(update_response.data)
        updated_data = {
            'name': 'Updated Stipend Name',
            'description': test_stipend.description,
            'amount': test_stipend.amount,
            'currency': test_stipend.currency,
            'csrf_token': csrf_token
        }
        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data, follow_redirects=True)

        assert response.status_code == 200
        updated_stipend = db_session.get(Stipend, test_stipend.id)
        assert updated_stipend.name == 'Updated Stipend Name'

def test_create_stipend_route_with_duplicate_name(logged_in_admin, test_stipend, stipend_data):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.stipend.create'))
        assert response.status_code == 200

        csrf_token = extract_csrf_token(response.data)
        duplicate_data = {
            'name': test_stipend.name,
            'description': "DuplicateDescription",
            'amount': 1500,
            'currency': "EUR",
            'csrf_token': csrf_token
        }
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=duplicate_data, follow_redirects=True)

        assert response.status_code == 200
        form = StipendForm(data=duplicate_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
    
        # Check that the stipend was not created
        new_stipend = db_session.query(Stipend).filter_by(name=duplicate_data['name']).first()
        assert new_stipend.id == test_stipend.id  # Ensure it's the same stipend

def test_create_stipend_route_with_csrf_token(logged_in_admin, stipend_data):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.stipend.create'))
        assert response.status_code == 200
        csrf_token = extract_csrf_token(response.data)
        assert csrf_token is not None
