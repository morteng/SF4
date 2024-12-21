from flask import url_for, render_template_string
import logging  # Import the logging module
from app.models.stipend import Stipend
from tests.conftest import logged_in_admin, db_session, stipend_data
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_ERROR, FLASH_CATEGORY_SUCCESS  # Import the constants

def test_create_stipend_with_invalid_form_data_htmx(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['name'] = ''  # Intentionally invalid
        stipend_data.setdefault('summary', 'Test Summary')
        stipend_data.setdefault('description', 'Test Description')
        stipend_data.setdefault('homepage_url', 'http://example.com')
        stipend_data.setdefault('application_procedure', 'Apply online')
        stipend_data.setdefault('eligibility_criteria', 'Open to all')
        stipend_data.setdefault('application_deadline', '2023-12-31 23:59:59')
        stipend_data.setdefault('open_for_applications', True)
        stipend_data.setdefault('submit', 'Create')

        response = logged_in_admin.post(
            url_for('admin.stipend.create'),
            data=stipend_data,
            headers={
                'HX-Request': 'true',
                'HX-Target': '#stipend-form-container'
            }
        )

        assert response.status_code == 200

        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None

        # Check if the flash message is present in the response data
        assert b'This field is required.' in response.data, "Flash message 'This field is required.' not found in response."

def test_create_stipend_with_invalid_application_deadline(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['application_deadline'] = '2023-13-32 99:99:99'
        response = logged_in_admin.post(
            url_for('admin.stipend.create'),
            data=stipend_data,
            headers={
                'HX-Request': 'true',
                'HX-Target': '#stipend-form-container'
            }
        )

        assert response.status_code == 200

        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        
        assert any(
            cat == FLASH_CATEGORY_ERROR and msg == FLASH_MESSAGES["INVALID_DATE_FORMAT"]
            for cat, msg in flashed_messages
        )

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
        response = logged_in_admin.post(
            url_for('admin.stipend.edit', id=test_stipend.id),
            data=updated_data,
            headers=headers
        )
        
        assert response.status_code == 200

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        
        assert any(
            cat == FLASH_CATEGORY_ERROR and msg == FLASH_MESSAGES["UPDATE_STIPEND_ERROR"]
            for cat, msg in flashed_messages
        )

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
        response = logged_in_admin.post(
            url_for('admin.stipend.edit', id=test_stipend.id),
            data=updated_data,
            headers=headers
        )
        
        assert response.status_code == 200

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        
        assert any(
            cat == FLASH_CATEGORY_ERROR and msg == 'This field is required.'
            for cat, msg in flashed_messages
        )
