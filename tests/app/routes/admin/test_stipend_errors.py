# tests/app/routes/admin/test_stipend_errors.py
import pytest
from flask import url_for
from app.models.stipend import Stipend
from app.forms.admin_forms import StipendForm
from datetime import datetime, timedelta
from tests.conftest import logged_in_admin, db_session, test_stipend, stipend_data

def test_create_stipend_with_database_error(stipend_data, logged_in_admin, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_add(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'add', mock_add)
        
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code in (200, 302)

        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None

def test_update_stipend_with_database_error(logged_in_admin, test_stipend, stipend_data, db_session, monkeypatch):
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

def test_delete_stipend_with_database_error(logged_in_admin, test_stipend, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.stipend.delete', id=test_stipend.id))
        
        assert response.status_code in (200, 302)

        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend is not None
