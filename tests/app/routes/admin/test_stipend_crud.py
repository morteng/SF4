# tests/app/routes/admin/test_stipend_crud.py
import pytest
from flask import url_for
from app.models.stipend import Stipend
from app.forms.admin_forms import StipendForm
from datetime import datetime, timedelta
from tests.conftest import logged_in_admin, db_session, test_stipend, stipend_data

def test_create_stipend(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code in (200, 302)

        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.summary == 'This is a test stipend.'
        assert stipend.description == 'Detailed description of the test stipend.'
        assert stipend.homepage_url == 'http://example.com/stipend'
        assert stipend.application_procedure == 'Apply online at example.com'
        assert stipend.eligibility_criteria == 'Open to all students'
        assert stipend.open_for_applications is True
        assert stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2023-12-31 23:59:59'

def test_update_stipend(logged_in_admin, test_stipend, stipend_data, db_session):
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

        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)
        
        assert response.status_code in (200, 302)

        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.name == updated_data['name']
        assert stipend.summary == "Updated summary."
        assert stipend.description == "Updated description."
        assert stipend.homepage_url == "http://example.com/updated-stipend"
        assert stipend.application_procedure == "Apply online at example.com/updated"
        assert stipend.eligibility_criteria == "Open to all updated students"
        assert stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2024-12-31 23:59:59'
        assert stipend.open_for_applications is True

def test_delete_stipend(logged_in_admin, test_stipend, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.stipend.delete', id=test_stipend.id))
        
        assert response.status_code in (200, 302)

        stipend = db_session.get(Stipend, test_stipend.id)
        assert stipend is None

def test_update_stipend_with_invalid_application_deadline(logged_in_admin, test_stipend, stipend_data, db_session):
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
        assert stipend.application_deadline == test_stipend.application_deadline
        assert b"Invalid date format" not in response.data  # Ensure no lingering error messages
