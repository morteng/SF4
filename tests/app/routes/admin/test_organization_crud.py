import pytest
from flask import url_for
from flask.testing import FlaskClient
from sqlalchemy.orm import Session
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy.exc import SQLAlchemyError
from app.models.organization import Organization
from app.constants import FlashMessages
from tests.conftest import logged_in_admin, db_session, organization_data
import re

def extract_csrf_token(response_data):
    csrf_regex = r'<input[^>]+name="csrf_token"[^>]+value="([^"]+)"'
    match = re.search(csrf_regex, response_data.decode('utf-8'))
    return match.group(1) if match else None

def test_organization_crud_workflow(logged_in_admin: FlaskClient, db_session: Session) -> None:
    create_response = logged_in_admin.post(
        url_for('admin.organization.create'),
        data={
            'name': 'Test Org',
            'description': 'Test Description',
            'homepage_url': 'http://test.org',
            'csrf_token': extract_csrf_token(logged_in_admin.get(url_for('admin.organization.create')).data)
        },
    )
    assert create_response.status_code == 302

    org = Organization.query.filter_by(name='Test Org').first()
    assert org is not None

    update_response = logged_in_admin.post(
        url_for('admin.organization.edit', id=org.id),
        data={
            'name': 'Updated Org',
            'description': 'Updated Description',
            'homepage_url': 'http://updated.org',
            'csrf_token': extract_csrf_token(
                logged_in_admin.get(url_for('admin.organization.edit', id=org.id)).data
            ),
        },
    )
    assert update_response.status_code == 302
    updated_org = Organization.query.get(org.id)
    assert updated_org.name == 'Updated Org'

    delete_response = logged_in_admin.post(url_for('admin.organization.delete', id=org.id))
    assert delete_response.status_code == 302
    assert Organization.query.get(org.id) is None

    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.organization.create'))
        assert response.status_code == 200
        assert b"Create Organization" in response.data

        csrf_token = extract_csrf_token(response.data)
        assert csrf_token

        data = organization_data.copy()
        data['csrf_token'] = csrf_token
        data['submit'] = 'Create'
        data['_csrf_token'] = csrf_token

        assert 'name' in data and data['name']
        assert 'description' in data
        assert 'homepage_url' in data

        response = logged_in_admin.post(url_for('admin.organization.create'), data=data)
        assert response.status_code == 302

        expected_url = url_for('admin.organization.index', _external=False)
        print(f"Expected URL: {expected_url}")

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])

        print("Flashed Messages:", flashed_messages)

        expected_flash_message = FlashMessages.CREATE_ORGANIZATION_SUCCESS.value
        assert any(cat == 'success' and msg == expected_flash_message for cat, msg in flashed_messages)

        follow_response = logged_in_admin.get(response.location)
        assert follow_response.status_code == 200

        new_organization = db_session.query(Organization).filter_by(name=data['name']).first()
        assert new_organization is not None
        assert new_organization.name == data['name']
        assert new_organization.description == data['description']
        assert new_organization.homepage_url == data['homepage_url']

def test_create_organization_with_invalid_form_data(logged_in_admin: FlaskClient, db_session: Session) -> None:
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        invalid_data = {
            'name': '',
            'description': 'This is a test organization.',
            'homepage_url': 'http://example.com/organization',
            'csrf_token': csrf_token,
            'submit': 'Create'
        }

        response = logged_in_admin.post(url_for('admin.organization.create'), data=invalid_data)
        assert response.status_code == 422
        assert b'Create Organization' in response.data

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        assert any(cat == 'error' and 'Name is required.' in msg for cat, msg in flashed_messages)

        new_organization = db_session.query(Organization).filter_by(name=invalid_data['name']).first()
        assert new_organization is None

def test_create_organization_with_duplicate_name(logged_in_admin: FlaskClient, db_session: Session, organization_data: dict) -> None:
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.organization.create'), data=organization_data)
        assert response.status_code == 302

        response = logged_in_admin.post(url_for('admin.organization.create'), data=organization_data)
        assert response.status_code == 200

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        expected_flash_message = FlashMessages.CREATE_ORGANIZATION_DUPLICATE_ERROR.value
        assert any(cat == 'error' and msg == expected_flash_message for cat, msg in flashed_messages)

def test_create_organization_with_long_name(logged_in_admin: FlaskClient, db_session: Session) -> None:
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        long_name = 'A' * 101
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
        assert any(cat == 'error' and 'Name cannot exceed 100 characters.' in msg for cat, msg in flashed_messages)

def test_create_organization_with_invalid_url(logged_in_admin: FlaskClient, db_session: Session) -> None:
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
        assert any(cat == 'error' and 'Homepage URL must be a valid URL.' in msg for cat, msg in flashed_messages)

        new_organization = db_session.query(Organization).filter_by(name=invalid_data['name']).first()
        assert new_organization is None

def test_create_organization_with_empty_form(logged_in_admin: FlaskClient, db_session: Session) -> None:
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
        assert any(cat == 'error' and 'Name is required.' in msg for cat, msg in flashed_messages)

def test_create_organization_with_database_rollback(
    logged_in_admin: FlaskClient,
    db_session: Session,
    organization_data: dict,
    monkeypatch: MonkeyPatch
) -> None:
    with logged_in_admin.application.app_context():
        def mock_commit(*args, **kwargs):
            raise SQLAlchemyError("Database error")

        monkeypatch.setattr(db_session, 'commit', mock_commit)

        response = logged_in_admin.post(url_for('admin.organization.create'), data=organization_data)
        assert response.status_code == 200

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        expected_flash_message = FlashMessages.CREATE_ORGANIZATION_DATABASE_ERROR.value
        assert any(cat == 'error' and msg == expected_flash_message for cat, msg in flashed_messages)

        new_organization = db_session.query(Organization).filter_by(name=organization_data['name']).first()
        assert new_organization is None

def test_create_organization_without_csrf_token(
    logged_in_admin: FlaskClient,
    db_session: Session,
    organization_data: dict
) -> None:
    with logged_in_admin.application.app_context():
        data = organization_data.copy()
        del data['csrf_token']

        response = logged_in_admin.post(url_for('admin.organization.create'), data=data)
        assert response.status_code in [400, 302]  # Different Flask versions handle this differently

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        assert any(cat == 'error' and 'CSRF token is missing' in msg for cat, msg in flashed_messages)
        assert any(cat == 'error' and 'The CSRF token is missing.' in msg for cat, msg in flashed_messages)

def test_create_organization_with_database_error(
    logged_in_admin: FlaskClient,
    organization_data: dict,
    db_session: Session,
    monkeypatch: MonkeyPatch
) -> None:
    with logged_in_admin.application.app_context():
        def mock_commit(*args, **kwargs):
            raise SQLAlchemyError("Database error")

        monkeypatch.setattr(db_session, 'commit', mock_commit)

        response = logged_in_admin.post(url_for('admin.organization.create'), data=organization_data)
        assert response.status_code == 200

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        expected_flash_message = FlashMessages.CREATE_ORGANIZATION_DATABASE_ERROR.value
        assert any(cat == 'error' and msg == expected_flash_message for cat, msg in flashed_messages)

        follow_response = logged_in_admin.get(response.location)
        assert follow_response.status_code == 200

def test_delete_organization_with_database_error(
    logged_in_admin: FlaskClient,
    db_session: Session,
    monkeypatch: MonkeyPatch
) -> None:
    with logged_in_admin.application.app_context():
        new_org = Organization(name="Org ID 1", description="Testing", homepage_url="http://example.org")
        db_session.add(new_org)
        db_session.commit()

        def mock_delete(*args, **kwargs):
            raise SQLAlchemyError("Database error")
        monkeypatch.setattr("app.routes.admin.organization_routes.delete_organization", mock_delete)

        response = logged_in_admin.post(url_for('admin.organization.delete', id=new_org.id))
        assert response.status_code == 302

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        expected_flash_message = FlashMessages.DELETE_ORGANIZATION_DATABASE_ERROR.value
        assert any(cat == 'error' and msg == expected_flash_message for cat, msg in flashed_messages)

        follow_response = logged_in_admin.get(response.location)
        assert follow_response.status_code == 200

def test_update_organization_with_database_error(
    logged_in_admin: FlaskClient,
    db_session: Session,
    monkeypatch: MonkeyPatch
) -> None:
    with logged_in_admin.application.app_context():
        new_org = Organization(name="Test Org", description="Initial Description", homepage_url="http://example.com")
        db_session.add(new_org)
        db_session.commit()
        organization_id = new_org.id

        update_data = {
            'name': 'Updated Organization',
            'description': 'This is an updated organization.',
            'homepage_url': 'http://example.com/updated-organization'
        }

        def mock_update(*args, **kwargs):
            raise SQLAlchemyError("Database error")
        monkeypatch.setattr("app.routes.admin.organization_routes.update_organization", mock_update)

        response = logged_in_admin.post(url_for('admin.organization.edit', id=organization_id), data=update_data)
        assert response.status_code == 302

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        expected_flash_message = FlashMessages.UPDATE_ORGANIZATION_DATABASE_ERROR.value
        assert any(cat == 'error' and msg == expected_flash_message for cat, msg in flashed_messages)

        follow_response = logged_in_admin.get(response.location)
        assert follow_response.status_code == 200

def test_update_organization_with_invalid_form_data(logged_in_admin: FlaskClient, db_session: Session) -> None:
    with logged_in_admin.application.app_context():
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

        response = logged_in_admin.post(url_for('admin.organization.edit', id=org.id), data=invalid_data)
        assert response.status_code == 422
        assert b'Edit Organization' in response.data

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        print("Flashed Messages:", flashed_messages)
        assert any(cat == 'error' and 'Name is required.' in msg for cat, msg in flashed_messages)

        org = db_session.query(Organization).filter_by(id=org.id).first()
        assert org.name != invalid_data['name']

def test_create_organization_with_empty_description(logged_in_admin: FlaskClient, db_session: Session) -> None:
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        invalid_data = {
            'name': 'Test Organization',
            'description': '',
            'homepage_url': 'http://example.com/organization',
            'csrf_token': csrf_token,
            'submit': 'Create'
        }

        response = logged_in_admin.post(url_for('admin.organization.create'), data=invalid_data)
        assert response.status_code == 422
        assert b'Create Organization' in response.data

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        assert any(cat == 'error' and 'About: This field is required.' in msg for cat, msg in flashed_messages)

def test_delete_organization(logged_in_admin: FlaskClient, db_session: Session) -> None:
    with logged_in_admin.application.app_context():
        org = Organization(name="Test Org", description="Initial Description", homepage_url="http://example.com")
        db_session.add(org)
        db_session.commit()

        response = logged_in_admin.post(url_for('admin.organization.delete', id=org.id))
        assert response.status_code == 302

        with logged_in_admin.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
        print("Flashed Messages:", flashed_messages)

        expected_flash_message = FlashMessages.DELETE_ORGANIZATION_SUCCESS.value
        assert any(cat == 'success' and msg == expected_flash_message for cat, msg in flashed_messages)

        follow_response = logged_in_admin.get(response.location)
        assert follow_response.status_code == 200

        org = db_session.query(Organization).filter_by(id=org.id).first()
        assert org is None
