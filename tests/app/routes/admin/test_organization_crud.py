#remove unnecessary comments AI!
import pytest
from flask import url_for
from app.models.organization import Organization
from app.forms.admin_forms import OrganizationForm
from tests.conftest import logged_in_admin, db_session, test_organization, organization_data
import re
import pytz
from sqlalchemy.exc import SQLAlchemyError
from app.constants import FLASH_MESSAGES

def extract_csrf_token(response_data):
    csrf_regex = r'<input[^>]+name="csrf_token"[^>]+value="([^"]+)"'
    match = re.search(csrf_regex, response_data.decode('utf-8'))
    if match:
        return match.group(1)
    return None

def test_create_organization(logged_in_admin, db_session, organization_data):
    """Test successful organization creation workflow"""
    with logged_in_admin.application.app_context():
        # Get CSRF token from the form
        response = logged_in_admin.get(url_for('admin.organization.create'))
        assert response.status_code == 200
        assert b"Create Organization" in response.data
        
        csrf_token = extract_csrf_token(response.data)
        assert csrf_token, "CSRF token not found in form"

        # Include CSRF token and form submit in the POST data
        data = organization_data.copy()
        data['csrf_token'] = csrf_token
        data['submit'] = 'Create'  # Add the submit button value
        
        # Ensure all required fields are present
        assert 'name' in data and data['name'], "Organization name is required"
        assert 'description' in data, "Description is required"
        assert 'homepage_url' in data, "Homepage URL is required"

        # Submit the form
        response = logged_in_admin.post(url_for('admin.organization.create'), data=data)
        assert response.status_code == 302

        expected_url = url_for('admin.organization.index', _external=False)
        print(f"Expected URL: {expected_url}")

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])

        print("Flashed Messages:", flashed_messages)

        expected_flash_message = FLASH_MESSAGES["CREATE_ORGANIZATION_SUCCESS"]
        assert any(
            cat == 'success' and msg == expected_flash_message
            for cat, msg in flashed_messages
        ), f"Flash message not found in session. Expected: {expected_flash_message}"

        follow_response = logged_in_admin.get(response.location)
        assert follow_response.status_code == 200

        new_organization = db_session.query(Organization).filter_by(name=data['name']).first()
        assert new_organization is not None
        assert new_organization.name == data['name']
        assert new_organization.description == data['description']
        assert new_organization.homepage_url == data['homepage_url']

def test_create_organization_with_invalid_form_data(logged_in_admin, db_session):
    """Test that invalid form data is properly handled."""
    with logged_in_admin.application.app_context():
        # Get CSRF token from the form
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        # Prepare invalid data
        invalid_data = {
            'name': '',
            'description': 'This is a test organization.',
            'homepage_url': 'http://example.com/organization',
            'csrf_token': csrf_token,
            'submit': 'Create'
        }

        # Submit the form
        response = logged_in_admin.post(url_for('admin.organization.create'), data=invalid_data)
        assert response.status_code == 422

        # Check that we're still on the form page
        assert b'Create Organization' in response.data

        # Inspect session for flash messages
        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])

        # Verify the correct error message is displayed
        assert any(
            cat == 'error' and 'Name is required.' in msg
            for cat, msg in flashed_messages
        ), "Field validation error not found in flash messages"

        # Ensure no organization was created
        new_organization = db_session.query(Organization).filter_by(name=invalid_data['name']).first()
        assert new_organization is None

def test_create_organization_with_duplicate_name(logged_in_admin, db_session, organization_data):
    """Test that duplicate organization names are rejected."""
    with logged_in_admin.application.app_context():
        # Create first organization
        response = logged_in_admin.post(url_for('admin.organization.create'), data=organization_data)
        assert response.status_code == 302

        # Attempt to create duplicate organization
        response = logged_in_admin.post(url_for('admin.organization.create'), data=organization_data)
        assert response.status_code == 200

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])

        expected_flash_message = FLASH_MESSAGES["CREATE_ORGANIZATION_DUPLICATE_ERROR"]
        assert any(
            cat == 'error' and msg == expected_flash_message
            for cat, msg in flashed_messages
        ), f"Flash message not found in session. Expected: {expected_flash_message}"

def test_create_organization_with_long_name(logged_in_admin, db_session):
    """Test that long organization names are rejected."""
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        long_name = 'A' * 101  # Exceeds the 100-character limit
        invalid_data = {
            'name': long_name,
            'description': 'This is a test organization.',
            'homepage_url': 'http://example.com/organization',
            'csrf_token': csrf_token,
            'submit': 'Create'
        }

        response = logged_in_admin.post(url_for('admin.organization.create'), data=invalid_data)
        assert response.status_code == 422

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])

        assert any(
            cat == 'error' and 'Name cannot exceed 100 characters.' in msg
            for cat, msg in flashed_messages
        ), "Field validation error not found in flash messages"

def test_create_organization_with_invalid_url(logged_in_admin, db_session):
    """Test that invalid URLs are rejected."""
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        invalid_data = {
            'name': 'Test Organization',
            'description': 'This is a test organization.',
            'homepage_url': 'invalid-url',
            'csrf_token': csrf_token,
            'submit': 'Create'
        }

        response = logged_in_admin.post(url_for('admin.organization.create'), data=invalid_data)
        assert response.status_code == 422

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])

        assert any(
            cat == 'error' and 'Homepage URL must be a valid URL.' in msg
            for cat, msg in flashed_messages
        ), "Field validation error not found in flash messages"

        # Ensure no organization was created
        new_organization = db_session.query(Organization).filter_by(name=invalid_data['name']).first()
        assert new_organization is None

def test_create_organization_with_empty_form(logged_in_admin, db_session):
    """Test that empty form submissions are rejected."""
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        invalid_data = {
            'name': '',
            'description': '',
            'homepage_url': '',
            'csrf_token': csrf_token,
            'submit': 'Create'
        }

        response = logged_in_admin.post(url_for('admin.organization.create'), data=invalid_data)
        assert response.status_code == 422

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])

        assert any(
            cat == 'error' and 'Name is required.' in msg
            for cat, msg in flashed_messages
        ), "Field validation error not found in flash messages"

def test_create_organization_with_database_rollback(logged_in_admin, db_session, organization_data, monkeypatch):
    """Test that database rollback works correctly in case of errors."""
    with logged_in_admin.application.app_context():
        def mock_commit(*args, **kwargs):
            raise SQLAlchemyError("Database error")

        monkeypatch.setattr(db_session, 'commit', mock_commit)

        response = logged_in_admin.post(url_for('admin.organization.create'), data=organization_data)
        assert response.status_code == 200

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])

        expected_flash_message = FLASH_MESSAGES['CREATE_ORGANIZATION_DATABASE_ERROR']
        assert any(
            cat == 'error' and msg == expected_flash_message
            for cat, msg in flashed_messages
        ), f"Flash message not found in session. Expected: {expected_flash_message}"

        # Ensure no organization was created
        new_organization = db_session.query(Organization).filter_by(name=organization_data['name']).first()
        assert new_organization is None

def test_create_organization_without_csrf_token(logged_in_admin, db_session, organization_data):
    """Test that CSRF protection is working correctly."""
    with logged_in_admin.application.app_context():
        # Remove CSRF token from data
        data = organization_data.copy()
        del data['csrf_token']

        response = logged_in_admin.post(url_for('admin.organization.create'), data=data)
        assert response.status_code in [400, 302]  # Different Flask versions may handle this differently

        # Check for CSRF error message
        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
            
        assert any(
            cat == 'error' and 'CSRF token is missing' in msg
            for cat, msg in flashed_messages
        ), "CSRF validation error not found in flash messages"

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])

        assert any(
            cat == 'error' and 'The CSRF token is missing.' in msg
            for cat, msg in flashed_messages
        ), "CSRF validation error not found in flash messages"

def test_create_organization_with_database_error(logged_in_admin, organization_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        data = organization_data

        def mock_commit(*args, **kwargs):
            raise SQLAlchemyError("Database error")

        monkeypatch.setattr(db_session, 'commit', mock_commit)

        # Remove follow_redirects=True so the flash stays in the session.
        response = logged_in_admin.post(url_for('admin.organization.create'), data=data)

        # Expect form re-render (200) for invalid data
        assert response.status_code == 200

        # Inspect session for flash messages
        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])  # returns list of (category, message) pairs

        expected_flash_message = FLASH_MESSAGES['CREATE_ORGANIZATION_DATABASE_ERROR']
        assert any(
            cat == 'error' and msg == expected_flash_message
            for cat, msg in flashed_messages
        ), f"Flash message not found in session. Expected: {expected_flash_message}"

        # Confirm the final page after redirect
        follow_response = logged_in_admin.get(response.location)
        assert follow_response.status_code == 200

def test_delete_organization_with_database_error(logged_in_admin, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        # Create org
        new_org = Organization(name="Org ID 1", description="Testing", homepage_url="http://example.org")
        db_session.add(new_org)
        db_session.commit()

        # Monkeypatch the delete_organization in the organization_routes module
        def mock_delete(*args, **kwargs):
            raise SQLAlchemyError("Database error")
        monkeypatch.setattr("app.routes.admin.organization_routes.delete_organization", mock_delete)

        # Attempt delete
        # Remove follow_redirects=True so the flash stays in the session.
        response = logged_in_admin.post(url_for('admin.organization.delete', id=new_org.id))

        # Expect a redirect (302), not a 200.
        assert response.status_code == 302

        # Inspect session for flash messages
        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])  # returns list of (category, message) pairs

        expected_flash_message = FLASH_MESSAGES['DELETE_ORGANIZATION_DATABASE_ERROR']
        assert any(
            cat == 'error' and msg == expected_flash_message
            for cat, msg in flashed_messages
        ), f"Flash message not found in session. Expected: {expected_flash_message}"

        # Confirm the final page after redirect
        follow_response = logged_in_admin.get(response.location)
        assert follow_response.status_code == 200

def test_update_organization_with_database_error(logged_in_admin, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        # Create an organization first
        new_org = Organization(
            name="Test Org",
            description="Initial Description",
            homepage_url="http://example.com"
        )
        db_session.add(new_org)
        db_session.commit()
        organization_id = new_org.id

        update_data = {
            'name': 'Updated Organization',
            'description': 'This is an updated organization.',
            'homepage_url': 'http://example.com/updated-organization'
        }

        # Monkeypatch the update_organization in the organization_routes module
        def mock_update(*args, **kwargs):
            raise SQLAlchemyError("Database error")
        monkeypatch.setattr("app.routes.admin.organization_routes.update_organization", mock_update)

        # Attempt to update the organization
        # Remove follow_redirects=True so the flash stays in the session.
        response = logged_in_admin.post(
            url_for('admin.organization.edit', id=organization_id),
            data=update_data
        )

        # Expect a redirect (302), not a 200.
        assert response.status_code == 302

        # Inspect session for flash messages
        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])  # returns list of (category, message) pairs

        expected_flash_message = FLASH_MESSAGES['UPDATE_ORGANIZATION_DATABASE_ERROR']
        assert any(
            cat == 'error' and msg == expected_flash_message
            for cat, msg in flashed_messages
        ), f"Flash message not found in session. Expected: {expected_flash_message}"

        # Confirm the final page after redirect
        follow_response = logged_in_admin.get(response.location)
        assert follow_response.status_code == 200

def test_update_organization_with_invalid_form_data(logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        # Create an organization first
        org = Organization(name="Test Org", description="Initial Description", homepage_url="http://example.com")
        db_session.add(org)
        db_session.commit()

        response = logged_in_admin.get(url_for('admin.organization.edit', id=org.id))
        csrf_token = extract_csrf_token(response.data)

        invalid_data = {
            'name': '',
            'description': 'Updated Description',
            'homepage_url': 'http://example.com/updated',
            'csrf_token': csrf_token
        }

        # Remove follow_redirects=True so the flash stays in the session.
        response = logged_in_admin.post(url_for('admin.organization.edit', id=org.id), data=invalid_data)

        # Expect form re-render (422) for invalid data
        assert response.status_code == 422

        # Check that we're still on the form page
        assert b'Edit Organization' in response.data

        # Inspect session for flash messages
        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])  # returns list of (category, message) pairs

        # Print the flash messages to debug
        print("Flashed Messages:", flashed_messages)

        # Expect field-specific validation message
        assert any(
            cat == 'error' and 'Name is required.' in msg
            for cat, msg in flashed_messages
        ), "Field validation error not found in flash messages"

        # Ensure organization was not updated
        org = db_session.query(Organization).filter_by(id=org.id).first()
        assert org.name != invalid_data['name']


def test_create_organization_with_empty_description(logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        invalid_data = {
            'name': 'Test Organization',
            'description': '',  # Empty description
            'homepage_url': 'http://example.com/organization',
            'csrf_token': csrf_token,
            'submit': 'Create'
        }

        response = logged_in_admin.post(url_for('admin.organization.create'), data=invalid_data)
        assert response.status_code == 422
        assert b'Create Organization' in response.data

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        assert any(
            cat == 'error' and 'About: This field is required.' in msg
            for cat, msg in flashed_messages
        ), "Field validation error not found in flash messages"

def test_delete_organization(logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        # Create an organization first
        org = Organization(name="Test Org", description="Initial Description", homepage_url="http://example.com")
        db_session.add(org)
        db_session.commit()

        response = logged_in_admin.post(url_for('admin.organization.delete', id=org.id))

        # Expect a redirect (302), not a 200.
        assert response.status_code == 302

        # Inspect session for flash messages
        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])  # returns list of (category, message) pairs

        # Print the flash messages to debug
        print("Flashed Messages:", flashed_messages)

        expected_flash_message = FLASH_MESSAGES["DELETE_ORGANIZATION_SUCCESS"]
        assert any(
            cat == 'success' and msg == expected_flash_message
            for cat, msg in flashed_messages
        ), f"Flash message not found in session. Expected: {expected_flash_message}"

        # Confirm the final page after redirect
        follow_response = logged_in_admin.get(response.location)
        assert follow_response.status_code == 200

        # Ensure organization was deleted
        org = db_session.query(Organization).filter_by(id=org.id).first()
        assert org is None
