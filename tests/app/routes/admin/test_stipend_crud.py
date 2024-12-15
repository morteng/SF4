import pytest
from flask import url_for
from app.models.stipend import Stipend
from tests.conftest import logged_in_admin, db_session, test_stipend, stipend_data

def test_create_stipend_with_valid_data(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 302  # Redirect after successful creation
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is not None

def test_create_stipend_with_invalid_data_empty_name(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['name'] = ''
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 200  # Form re-renders
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None

def test_create_stipend_with_invalid_application_deadline(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['application_deadline'] = '2023-13-32 99:99:99'
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 200  # Form re-renders
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None

def test_update_stipend_with_valid_data(logged_in_admin, test_stipend, stipend_data, db_session):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': 'Updated Stipend',
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2025-12-31 23:59:59',
            'open_for_applications': True
        }
        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)
        
        assert response.status_code == 302  # Redirect after successful update
        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.name == updated_data['name']

def test_update_stipend_with_invalid_data_empty_name(logged_in_admin, test_stipend, stipend_data, db_session):
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
        
        assert response.status_code == 200  # Form re-renders
        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.name != updated_data['name']

def test_update_stipend_with_invalid_application_deadline(logged_in_admin, test_stipend, stipend_data, db_session):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': 'Updated Stipend',
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2023-13-32 99:99:99',
            'open_for_applications': True
        }
        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)
        
        assert response.status_code == 200  # Form re-renders
        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.application_deadline != updated_data['application_deadline']

def test_delete_stipend_with_valid_id(logged_in_admin, test_stipend, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.stipend.delete', id=test_stipend.id))
        
        assert response.status_code == 302  # Redirect after successful deletion
        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend is None

def test_delete_stipend_with_invalid_id(logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.stipend.delete', id=9999))
        
        assert response.status_code == 302  # Redirect even if deletion fails
