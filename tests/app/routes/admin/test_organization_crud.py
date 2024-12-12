import pytest
from flask import url_for, session, flash
from app.models.organization import Organization
from app.forms.admin_forms import OrganizationForm
from datetime import datetime, timedelta
from tests.conftest import logged_in_admin, db_session, test_organization, organization_data

def test_create_organization(logged_in_admin, db_session, organization_data):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.organization.create'), data=organization_data)
        
        assert response.status_code == 302
        assert url_for('admin.organization.index', _external=False) == response.headers['Location']

        # Check if the organization was created successfully
        new_organization = db_session.query(Organization).filter_by(name=organization_data['name']).first()
        assert new_organization is not None
        assert new_organization.name == organization_data['name']
        assert new_organization.description == organization_data['description']
        assert new_organization.homepage_url == organization_data['homepage_url']  # Ensure this line checks the correct field

def test_create_organization_with_invalid_form_data(logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        invalid_data = {
            'name': '',  # Intentionally invalid
            'description': 'Test Description',
            'homepage_url': 'http://example.com',
            'csrf_token': logged_in_admin.csrf_token  # Fetch CSRF token from the client session
        }
        
        response = logged_in_admin.post(url_for('admin.organization.create'), data=invalid_data)
        
        assert response.status_code == 200

        form = OrganizationForm(data=invalid_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
            
        # Check that the organization was not created
        new_organization = db_session.query(Organization).filter_by(name=invalid_data['name']).first()
        assert new_organization is None

def test_update_organization(logged_in_admin, test_organization, db_session):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': 'Updated Organization',
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-organization",
            'csrf_token': logged_in_admin.csrf_token  # Fetch CSRF token from the client session
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
        invalid_data = {
            'name': '',  # Intentionally invalid
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-organization",
            'csrf_token': logged_in_admin.csrf_token  # Fetch CSRF token from the client session
        }

        response = logged_in_admin.post(url_for('admin.organization.update', id=test_organization.id), data=invalid_data)
        
        assert response.status_code == 200

        form = OrganizationForm(data=invalid_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
            
        # Check that the organization was not updated
        db_session.expire_all()
        organization = db_session.query(Organization).filter_by(id=test_organization.id).first()
        assert organization.name != invalid_data['name']
        assert organization.description == test_organization.description
        assert organization.homepage_url == test_organization.homepage_url

def test_delete_organization(logged_in_admin, test_organization, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.organization.delete', id=test_organization.id))
        
        assert response.status_code == 302
        assert url_for('admin.organization.index', _external=False) == response.headers['Location']

        # Check if the organization was deleted successfully
        deleted_organization = db_session.query(Organization).filter_by(id=test_organization.id).first()
        assert deleted_organization is None

def test_delete_nonexistent_organization(logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.organization.delete', id=9999))
        
        assert response.status_code == 302
        assert url_for('admin.organization.index', _external=False) == response.headers['Location']

        # Check that no organization was deleted
        organizations_count = db_session.query(Organization).count()
        assert organizations_count == 0

def test_index_organizations(logged_in_admin, test_organization, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.organization.index'))
        
        assert response.status_code == 200
        assert b'Test Organization' in response.data  # Ensure the organization name is displayed

def test_create_organization_with_duplicate_name(logged_in_admin, db_session, test_organization):
    with logged_in_admin.application.app_context():
        duplicate_data = {
            'name': test_organization.name,
            'description': "Duplicate description.",
            'homepage_url': "http://example.com/duplicate-organization",
            'csrf_token': logged_in_admin.csrf_token  # Fetch CSRF token from the client session
        }
        
        response = logged_in_admin.post(url_for('admin.organization.create'), data=duplicate_data)
        
        assert response.status_code == 200

        form = OrganizationForm(data=duplicate_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
            
        # Check that the organization was not created
        new_organization = db_session.query(Organization).filter_by(name=duplicate_data['name']).first()
        assert new_organization.id == test_organization.id  # Ensure it's the same organization

def test_update_organization_with_duplicate_name(logged_in_admin, test_organization, db_session):
    with logged_in_admin.application.app_context():
        duplicate_data = {
            'name': test_organization.name,
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-organization",
            'csrf_token': logged_in_admin.csrf_token  # Fetch CSRF token from the client session
        }

        response = logged_in_admin.post(url_for('admin.organization.update', id=test_organization.id), data=duplicate_data)
        
        assert response.status_code == 302
        assert url_for('admin.organization.index', _external=False) == response.headers['Location']

        db_session.expire_all()
        organization = db_session.query(Organization).filter_by(id=test_organization.id).first()
        assert organization.name == duplicate_data['name']
        assert organization.description == duplicate_data['description']
        assert organization.homepage_url == duplicate_data['homepage_url']
