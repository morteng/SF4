# tests/app/routes/admin/test_stipend_htmx.py
import pytest
from flask import url_for
from app.models.stipend import Stipend
from app.forms.admin_forms import StipendForm
from datetime import datetime, timedelta
from tests.conftest import logged_in_admin, db_session, test_stipend, stipend_data

def test_create_stipend_with_invalid_form_data_htmx(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['name'] = ''  # Intentionally invalid
        # Ensure all required fields are present
        stipend_data.setdefault('summary', 'Test Summary')
        stipend_data.setdefault('description', 'Test Description')
        stipend_data.setdefault('homepage_url', 'http://example.com')
        stipend_data.setdefault('application_procedure', 'Apply online')
        stipend_data.setdefault('eligibility_criteria', 'Open to all')
        stipend_data.setdefault('application_deadline', '2023-12-31 23:59:59')
        stipend_data.setdefault('open_for_applications', True)
        stipend_data.setdefault('submit', 'Create')  # If your form expects a submit field

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

        # Optionally, check that the response contains the form with errors
        assert b'This field is required.' in response.data  # Adjust the error message as needed

def test_create_stipend_with_invalid_application_deadline_format_htmx(stipend_data, logged_in_admin, db_session):
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

        # Optionally, check that the response contains the form with errors
        assert b'Invalid date format. Please use YYYY-MM-DD HH:MM:SS.' in response.data

        assert b'id="stipend-form-container"' in response.data  # Validate target container exists

def test_update_stipend_with_database_error_htmx(logged_in_admin, test_stipend, stipend_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': test_stipend.name,
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2024-12-31 23:59:59',
            'open_for_applications': True
        }

        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)
        
        assert response.status_code in (200, 302)

        db_session.expire_all()
        stipend = db_session.merge(test_stipend)
        assert stipend is not None
        assert stipend.summary != "Updated summary."

def test_update_stipend_with_invalid_application_deadline_format_htmx(logged_in_admin, test_stipend, stipend_data, db_session):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': test_stipend.name,
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2023-13-32 99:99:99',
            'open_for_applications': True
        }

        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)
        
        assert response.status_code in (200, 302)

        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.application_deadline is None
