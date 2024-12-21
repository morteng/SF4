import pytest
from flask import url_for
from app.models.organization import Organization
from app.forms.admin_forms import OrganizationForm
from tests.conftest import logged_in_admin, db_session, test_organization, organization_data
import re
from sqlalchemy.exc import SQLAlchemyError
from app.constants import FLASH_MESSAGES

def extract_csrf_token(response_data):
    csrf_regex = r'<input[^>]+name="csrf_token"[^>]+value="([^"]+)"'
    match = re.search(csrf_regex, response_data.decode('utf-8'))
    if match:
        return match.group(1)
    return None

def test_create_organization(logged_in_admin, db_session, organization_data):
    with logged_in_admin.application.app_context():
        data = organization_data
        response = logged_in_admin.post(url_for('admin.organization.create'), data=data, follow_redirects=True)
        
        assert response.status_code == 200

        # Print the URL generated by url_for to debug
        expected_url = url_for('admin.organization.index', _external=False)
        print(f"Expected URL: {expected_url}")

        # Print the response data to debug
        print(response.get_data(as_text=True))

        assert expected_url in response.get_data(as_text=True)

        new_organization = db_session.query(Organization).filter_by(name=data['name']).first()
        assert new_organization is not None
        assert new_organization.name == data['name']
        assert new_organization.description == data['description']
        assert new_organization.homepage_url == data['homepage_url']

        # Check for success flash message
        assert FLASH_MESSAGES["CREATE_ORGANIZATION_SUCCESS"].encode() in response.data

def test_create_organization_with_invalid_form_data(logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        invalid_data = {
            'name': '',
            'description': 'This is a test organization.',
            'homepage_url': 'http://example.com/organization',
            'csrf_token': csrf_token
        }

        response = logged_in_admin.post(url_for('admin.organization.create'), data=invalid_data, follow_redirects=True)
        
        assert response.status_code == 200

        # Print the response data to debug
        print(response.get_data(as_text=True))

        expected_flash_message = 'name: This field is required.'
        assert expected_flash_message.encode() in response.data

def test_create_organization_with_database_error(logged_in_admin, organization_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        data = organization_data

        def mock_commit(*args, **kwargs):
            raise SQLAlchemyError("Database error")

        monkeypatch.setattr(db_session, 'commit', mock_commit)

        response = logged_in_admin.post(url_for('admin.organization.create'), data=data, follow_redirects=True)
        
        assert response.status_code == 200

        # Print the response data to debug
        print(response.get_data(as_text=True))

        expected_flash_message = FLASH_MESSAGES['CREATE_ORGANIZATION_DATABASE_ERROR'].format("Database error")
        assert expected_flash_message.encode() in response.data

def test_delete_organization_with_database_error(logged_in_admin, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        # Create and commit an organization with ID=1
        new_org = Organization(name="Org ID 1", description="Testing", homepage_url="http://example.org")
        db_session.add(new_org)
        db_session.commit()

        def mock_delete(*args, **kwargs):
            raise SQLAlchemyError("Database error")

        monkeypatch.setattr(db_session, 'delete', mock_delete)

        response = logged_in_admin.post(url_for('admin.organization.delete', id=new_org.id), follow_redirects=True)

        assert response.status_code == 200

        # Print the response data to debug
        print(response.get_data(as_text=True))

        expected_flash_message = FLASH_MESSAGES['DELETE_ORGANIZATION_DATABASE_ERROR'].format("Database error")
        assert expected_flash_message.encode() in response.data

def test_update_organization_with_database_error(logged_in_admin, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        organization_id = 1
        update_data = {
            'name': 'Updated Organization',
            'description': 'This is an updated organization.',
            'homepage_url': 'http://example.com/updated-organization'
        }

        def mock_commit(*args, **kwargs):
            raise SQLAlchemyError("Database error")

        monkeypatch.setattr(db_session, 'commit', mock_commit)

        response = logged_in_admin.post(url_for('admin.organization.edit', id=organization_id), data=update_data, follow_redirects=True)
        
        assert response.status_code == 200

        # Print the response data to debug
        print(response.get_data(as_text=True))

        expected_flash_message = FLASH_MESSAGES['UPDATE_ORGANIZATION_DATABASE_ERROR'].format("Database error")
        assert expected_flash_message.encode() in response.data

def test_delete_organization(logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        # Create a test organization
        data = {
            'name': 'Test Organization',
            'description': 'This is a test organization.',
            'homepage_url': 'http://example.com/organization'
        }
        response = logged_in_admin.post(url_for('admin.organization.create'), data=data, follow_redirects=True)
        
        assert response.status_code == 200

        # Get the created organization
        new_organization = db_session.query(Organization).filter_by(name='Test Organization').first()
        assert new_organization is not None

        # Delete the organization
        delete_response = logged_in_admin.post(url_for('admin.organization.delete', id=new_organization.id), follow_redirects=True)
        
        assert delete_response.status_code == 200

        # Check for success flash message
        assert FLASH_MESSAGES["DELETE_ORGANIZATION_SUCCESS"].encode() in delete_response.data

        # Verify the organization is deleted
        deleted_organization = db_session.query(Organization).filter_by(id=new_organization.id).first()
        assert deleted_organization is None
