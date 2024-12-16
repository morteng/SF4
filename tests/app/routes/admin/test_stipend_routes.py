from flask import url_for
from app.models.stipend import Stipend
from tests.conftest import logged_in_admin, stipend_data, test_stipend, db_session, monkeypatch
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR

def test_create_stipend_with_invalid_form_data(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['name'] = ''  # Intentionally invalid
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 200
        assert b"This field is required." in response.data
        assert b'Create Stipend' in response.data
        assert b'<input name="name"' in response.data

def test_create_stipend_with_none_result(stipend_data, logged_in_admin, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_create_stipend(*args, **kwargs):
            return None

        monkeypatch.setattr('app.services.stipend_service.create_stipend', mock_create_stipend)

        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["CREATE_STIPEND_ERROR"].encode() in response.data
        assert b'Create Stipend' in response.data
        assert b'<form' in response.data

def test_create_stipend_with_database_error(stipend_data, logged_in_admin, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["CREATE_STIPEND_ERROR"].encode() in response.data
        assert b'Create Stipend' in response.data
        assert b'<form' in response.data

def test_update_stipend_with_invalid_form_data(logged_in_admin, test_stipend, stipend_data, db_session):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': '',
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2025-12-31 23:59:59',
            'open_for_applications': True
        }
        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)
        
        assert response.status_code == 200
        assert b"This field is required." in response.data
        assert b'Edit Stipend' in response.data
        assert b'<input name="name"' in response.data

def test_update_stipend_with_database_error(logged_in_admin, test_stipend, stipend_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': test_stipend.name,
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2025-12-31 23:59:59',
            'open_for_applications': True
        }

        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["UPDATE_STIPEND_ERROR"].encode() in response.data
        assert b'Edit Stipend' in response.data
        assert b'<form' in response.data

def test_create_stipend_with_invalid_form_data_htmx(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['name'] = ''  # Intentionally invalid
        headers = {'HX-Request': 'true'}
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data, headers=headers)
        
        assert response.status_code == 200
        assert b"This field is required." in response.data
        assert b'id="stipend-form-container"' in response.data

def test_create_stipend_with_none_result_htmx(stipend_data, logged_in_admin, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_create_stipend(*args, **kwargs):
            return None

        monkeypatch.setattr('app.services.stipend_service.create_stipend', mock_create_stipend)

        headers = {'HX-Request': 'true'}
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data, headers=headers)
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["CREATE_STIPEND_ERROR"].encode() in response.data
        assert b'id="stipend-form-container"' in response.data

def test_create_stipend_with_database_error_htmx(stipend_data, logged_in_admin, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        headers = {'HX-Request': 'true'}
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data, headers=headers)
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["CREATE_STIPEND_ERROR"].encode() in response.data
        assert b'id="stipend-form-container"' in response.data

def test_update_stipend_with_invalid_form_data_htmx(logged_in_admin, test_stipend, stipend_data, db_session):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': '',
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2025-12-31 23:59:59',
            'open_for_applications': True
        }
        headers = {'HX-Request': 'true'}
        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data, headers=headers)
        
        assert response.status_code == 200
        assert b"This field is required." in response.data
        assert b'id="stipend-form-container"' in response.data

def test_update_stipend_with_database_error_htmx(logged_in_admin, test_stipend, stipend_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': test_stipend.name,
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2025-12-31 23:59:59',
            'open_for_applications': True
        }

        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        headers = {'HX-Request': 'true'}
        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data, headers=headers)
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["UPDATE_STIPEND_ERROR"].encode() in response.data
        assert b'id="stipend-form-container"' in response.data
