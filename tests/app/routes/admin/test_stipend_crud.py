import pytest
from flask import url_for
from app.models.stipend import Stipend
from app.forms.admin_forms import StipendForm  # Import the StipendForm class
from datetime import datetime, timedelta
from tests.conftest import logged_in_admin, db_session, test_stipend, stipend_data
import re

def extract_csrf_token(response_data):
    csrf_match = re.search(r'name="csrf_token" type="hidden" value="(.+?)"', response_data.decode('utf-8'))
    return csrf_match.group(1) if csrf_match else None  # Fallback

def test_create_stipend(logged_in_admin, db_session, stipend_data):
    with logged_in_admin.application.app_context():
        data = stipend_data
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=data)
        
        assert response.status_code == 302
        assert url_for('admin.stipend.index', _external=False) == response.headers['Location']

        new_stipend = db_session.query(Stipend).filter_by(name=data['name']).first()
        assert new_stipend is not None
        assert new_stipend.name == data['name']
        assert new_stipend.summary == data['summary']
        assert new_stipend.description == data['description']
        assert new_stipend.homepage_url == data['homepage_url']
        assert new_stipend.application_procedure == data['application_procedure']
        assert new_stipend.eligibility_criteria == data['eligibility_criteria']
        assert new_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2023-12-31 23:59:59'
        assert new_stipend.open_for_applications is True

def test_create_stipend_with_invalid_form_data(logged_in_admin, db_session, stipend_data):
    with logged_in_admin.application.app_context():
        # Call the stipend_data function to get the dictionary
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

def test_create_stipend_with_database_error(logged_in_admin, stipend_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        data = stipend_data

        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=data)
        
        assert response.status_code == 200

        # Check that the stipend was not created
        new_stipend = db_session.query(Stipend).filter_by(name=data['name']).first()
        assert new_stipend is None

def test_update_stipend(logged_in_admin, test_stipend, db_session, stipend_data):
    with logged_in_admin.application.app_context():
        updated_data = stipend_data
        updated_data.update({
            'name': "Updated Stipend",
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2024-12-31 23:59:59',
            'open_for_applications': True
        })

        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)
        
        assert response.status_code == 302

        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.name == updated_data['name']
        assert stipend.summary == updated_data['summary']
        assert stipend.description == updated_data['description']
        assert stipend.homepage_url == updated_data['homepage_url']
        assert stipend.application_procedure == updated_data['application_procedure']
        assert stipend.eligibility_criteria == updated_data['eligibility_criteria']
        assert stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2024-12-31 23:59:59'
        assert stipend.open_for_applications is True

def test_update_stipend_with_invalid_form_data(logged_in_admin, test_stipend, db_session, stipend_data):
    with logged_in_admin.application.app_context():
        updated_data = stipend_data
        
        # Intentionally make the name field invalid
        updated_data['name'] = ''
        
        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)
        
        assert response.status_code == 200

        form = StipendForm(data=updated_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
            
        # Check that the stipend was not updated
        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.name != updated_data['name']
        assert stipend.summary == test_stipend.summary

def test_update_stipend_with_database_error(logged_in_admin, test_stipend, stipend_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        updated_data = stipend_data
        updated_data.update({
            'name': test_stipend.name,
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2024-12-31 23:59:59',
            'open_for_applications': True
        })

        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)
        
        assert response.status_code == 200

        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.summary != "Updated summary."

def test_delete_stipend(logged_in_admin, test_stipend, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.stipend.delete', id=test_stipend.id))
        
        assert response.status_code == 302

        deleted_stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert deleted_stipend is None

def test_delete_stipend_with_database_error(logged_in_admin, test_stipend, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.stipend.delete', id=test_stipend.id))
        
        assert response.status_code == 302

        # Check that the stipend was not deleted
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend is not None
