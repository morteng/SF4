# tests/app/routes/admin/test_stipend_validation.py
import pytest
from flask import url_for
from app.models.stipend import Stipend
from app.forms.admin_forms import StipendForm
from datetime import datetime, timedelta
from tests.conftest import logged_in_admin, db_session, test_stipend, stipend_data

def test_create_stipend_with_blank_application_deadline(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['application_deadline'] = ''
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code in (200, 302)

        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.application_deadline is None

def test_create_stipend_with_invalid_application_deadline(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['application_deadline'] = '2023-13-32 99:99:99'
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 200  # Ensure form re-renders

        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None  # Ensure stipend is not created with invalid date
        assert b'Invalid date format. Please use YYYY-MM-DD HH:MM:SS.' in response.data

def test_update_stipend_with_blank_application_deadline(logged_in_admin, test_stipend, stipend_data, db_session):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': test_stipend.name,
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '',
            'open_for_applications': True
        }

        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)
        
        assert response.status_code in (200, 302)

        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.application_deadline is None

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
        assert b"Invalid date format. Please use YYYY-MM-DD HH:MM:SS." in response.data

def test_create_stipend_with_invalid_form_data(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['name'] = ''
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 200

        form = StipendForm(data=stipend_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
            
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None
