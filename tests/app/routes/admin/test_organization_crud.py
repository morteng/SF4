import pytest
from flask import url_for
from app.models.organization import Organization
from app.forms.admin_forms import OrganizationForm  # Import the StipendForm class
from datetime import datetime, timedelta
from tests.conftest import logged_in_admin, db_session, test_organization, organization_data
import re
from sqlalchemy.exc import SQLAlchemyError

def extract_csrf_token(response_data):
    """Extract CSRF token from the response HTML."""
    csrf_match = re.search(r'name="csrf_token" type="hidden" value="(.+?)"', response_data.decode('utf-8'))
    return csrf_match.group(1) if csrf_match else None  # Fallback

def test_create_organization(logged_in_admin, db_session, organization_data):
    with logged_in_admin.application.app_context():
        data = organization_data
        response = logged_in_admin.post(url_for('admin.organization.create'), data=data)
        
        assert response.status_code == 302
        assert url_for('admin.organization.index', _external=False) == response.headers['Location']

        new_organization = db_session.query(Organization).filter_by(name=data['name']).first()
        assert new_organization is not None
        assert new_organization.name == data['name']
        assert new_organization.description == data['description']
        assert new_organization.homepage_url == data['homepage_url']  # Ensure this line checks the correct field

def test_create_organization_with_invalid_form_data(logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        # Fetch CSRF token from the form page
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        invalid_data = {
            'name': '',  # Intentionally invalid
            'description': 'Test Description',
            'homepage_url': 'http://example.com',
            'csrf_token': csrf_token
        }
        
        response = logged_in_admin.post(url_for('admin.organization.create'), data=invalid_data)
        
        assert response.status_code == 200

        form = OrganizationForm(original_name=None, data=invalid_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
                
        # Check that the organization was not created
        new_organization = db_session.query(Organization).filter_by(name=invalid_data['name']).first()
        assert new_organization is None

def test_create_organization_with_database_error(logged_in_admin, organization_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        data = organization_data

        def mock_commit(*args, **kwargs):
            raise SQLAlchemyError("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.organization.create'), data=data)

        assert response.status_code == 200

        assert b"Failed to create organization. Error: Database error" in response.data



        organizations = db_session.query(Organization).all()
        assert not any(org.name == data['name'] for org in organizations)  # Ensure no organization was created

def test_update_organization(logged_in_admin, test_organization, db_session):
    with logged_in_admin.application.app_context():
        # Fetch CSRF token from the form page
        response = logged_in_admin.get(url_for('admin.organization.update', id=test_organization.id))
        csrf_token = extract_csrf_token(response.data)

        updated_data = {
            'name': 'Updated Organization',
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-organization",
            'csrf_token': csrf_token
        }

        response = logged_in_admin.post(url_for('admin.organization.update', id=test_organization.id), data=updated_data)
        
        assert response.status_code == 302
        assert url_for('admin.organization.index', _external=False) == response.headers['Location']

        db_session.expire_all()
        organization = db_session.query(Organization).filter_by(id=test_organization.id).first()
        assert organization.name == updated_data['name']
        assert organization.description == updated_data['description']
        assert organization.homepage_url == updated_data['homepage_url']  # Ensure this line checks the correct field

def test_update_organization_with_invalid_form_data(logged_in_admin, test_organization, db_session):
    with logged_in_admin.application.app_context():
        # Fetch CSRF token from the form page
        response = logged_in_admin.get(url_for('admin.organization.update', id=test_organization.id))
        csrf_token = extract_csrf_token(response.data)

        invalid_data = {
            'name': '',  # Intentionally invalid
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-organization",
            'csrf_token': csrf_token
        }

        response = logged_in_admin.post(url_for('admin.organization.update', id=test_organization.id), data=invalid_data)
        
        assert response.status_code == 200

        form = OrganizationForm(original_name=test_organization.name, data=invalid_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
            
        # Check that the organization was not updated
        db_session.expire_all()
        organization = db_session.query(Organization).filter_by(id=test_organization.id).first()
        assert organization.name != invalid_data['name']
        assert organization.description == test_organization.description
        assert organization.homepage_url == test_organization.homepage_url

def test_update_organization_with_invalid_id(logged_in_admin):
    update_response = logged_in_admin.get(url_for('admin.organization.update', id=9999))
    assert update_response.status_code == 302
    assert url_for('admin.organization.index', _external=False) == update_response.headers['Location']

def test_delete_organization(logged_in_admin, test_organization, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.organization.delete', id=test_organization.id))
        
        assert response.status_code == 302
        assert url_for('admin.organization.index', _external=False) == response.headers['Location']

        # Check if the organization was deleted successfully
        deleted_organization = db_session.query(Organization).filter_by(id=test_organization.id).first()
        assert deleted_organization is None

def test_delete_organization_with_invalid_id(logged_in_admin):
    delete_response = logged_in_admin.post(url_for('admin.organization.delete', id=9999))
    
    assert delete_response.status_code == 302
    assert url_for('admin.organization.index', _external=False) == delete_response.headers['Location']

def test_delete_nonexistent_organization(logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.organization.delete', id=9999))
        
        assert response.status_code == 302
        assert url_for('admin.organization.index', _external=False) == response.headers['Location']

def test_index_organization_route(logged_in_admin, test_organization):
    index_response = logged_in_admin.get(url_for('admin.organization.index'))
    assert index_response.status_code == 200
