# tests/app/routes/admin/test_stipend_routes.py

import pytest
from flask import url_for
from app.models.stipend import Stipend
from app.forms.admin_forms import StipendForm
from datetime import datetime, timedelta
from tests.conftest import logged_in_admin, db_session, test_stipend, stipend_data
from unittest.mock import patch

def test_create_stipend_with_invalid_form_data(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['name'] = ''  # Intentionally invalid
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 200

        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None

def test_create_stipend_with_none_result(stipend_data, logged_in_admin, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_create_stipend(*args, **kwargs):
            return None

        monkeypatch.setattr('app.routes.admin.stipend_routes.create_stipend', mock_create_stipend)

        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 200
        assert b"Stipend creation failed due to invalid input." in response.data

        stipends = db_session.query(Stipend).filter_by(name=stipend_data['name']).all()
        assert len(stipends) == 0  # Ensure no stipend was created

def test_create_stipend_with_database_error(stipend_data, logged_in_admin, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 200

        stipends = db_session.query(Stipend).filter_by(name=stipend_data['name']).all()
        assert len(stipends) == 0  # Ensure no stipend was created
        assert b"Failed to create stipend. Please try again." in response.data

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

        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.name != ''  # Ensure the name was not updated

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

        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.summary != "Updated summary."
