from flask import url_for
from app.models.tag import Tag
from tests.conftest import logged_in_admin, tag_data, extract_csrf_token, get_all_tags
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR
from sqlalchemy.exc import IntegrityError
import pytest
from app.services.tag_service import create_tag

def test_create_tag_get_request(logged_in_admin):
    response = logged_in_admin.get(url_for('admin.tag.create'))
    assert response.status_code == 200
    assert b'Create Tag' in response.data

def test_create_tag_with_valid_data(logged_in_admin, tag_data):
    create_response = logged_in_admin.get(url_for('admin.tag.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    response = logged_in_admin.post(url_for('admin.tag.create'), data={
        'name': tag_data['name'],
        'category': tag_data['category'],
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    tags = get_all_tags()
    assert any(tag.name == tag_data['name'] and tag.category == tag_data['category'] for tag in tags)
    assert FLASH_MESSAGES["CREATE_TAG_SUCCESS"].encode() in response.data

def test_create_tag_with_invalid_form_data(logged_in_admin):
    create_response = logged_in_admin.get(url_for('admin.tag.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    response = logged_in_admin.post(url_for('admin.tag.create'), data={
        'name': '',  # Invalid name
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    assert FLASH_MESSAGES["GENERIC_ERROR"].encode() in response.data

def test_create_tag_with_integrity_error(logged_in_admin, tag_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_create_tag(*args, **kwargs):
            raise IntegrityError("test", {}, None)

        # Corrected monkeypatch target
        monkeypatch.setattr('app.routes.admin.tag_routes.create_tag', mock_create_tag)

        # Extract CSRF token
        create_response = logged_in_admin.get(url_for('admin.tag.create'))
        csrf_token = extract_csrf_token(create_response.data)

        # Include CSRF token in POST data
        response = logged_in_admin.post(url_for('admin.tag.create'), data={
            'name': tag_data['name'],
            'category': tag_data['category'],
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200
        assert FLASH_MESSAGES["CREATE_TAG_ERROR"].encode() in response.data

def test_delete_nonexistent_tag(logged_in_admin):
    # Attempt to delete a tag that does not exist
    response = logged_in_admin.post(url_for('admin.tag.delete', id=9999), follow_redirects=True)
    assert response.status_code == 200
    assert FLASH_MESSAGES["GENERIC_ERROR"].encode() in response.data

def test_delete_tag_with_integrity_error(logged_in_admin, tag_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        # Create a tag to delete
        new_tag = create_tag(tag_data)
        db_session.commit()

        def mock_commit(*args, **kwargs):
            raise IntegrityError("test", {}, None)

        monkeypatch.setattr(db_session, 'commit', mock_commit)

        response = logged_in_admin.post(url_for('admin.tag.delete', id=new_tag.id), follow_redirects=True)
        assert response.status_code == 200
        assert FLASH_MESSAGES["DELETE_TAG_ERROR"].encode() in response.data

def test_index_route(logged_in_admin, tag_data, db_session):
    with logged_in_admin.application.app_context():
        # Create a tag to list
        new_tag = create_tag(tag_data)
        db_session.commit()

        response = logged_in_admin.get(url_for('admin.tag.index'))
        assert response.status_code == 200
        assert new_tag.name.encode() in response.data

def test_update_tag_get_request(logged_in_admin, tag_data, db_session):
    with logged_in_admin.application.app_context():
        # Create a tag to update
        new_tag = create_tag(tag_data)
        db_session.commit()

        response = logged_in_admin.get(url_for('admin.tag.edit', id=new_tag.id))
        assert response.status_code == 200
        assert b'Update Tag' in response.data

def test_update_tag_with_valid_data(logged_in_admin, tag_data, db_session):
    with logged_in_admin.application.app_context():
        # Create a tag to update
        new_tag = create_tag(tag_data)
        db_session.commit()

        update_response = logged_in_admin.get(url_for('admin.tag.edit', id=new_tag.id))
        assert update_response.status_code == 200

        csrf_token = extract_csrf_token(update_response.data)
        updated_data = {
            'name': tag_data['name'],
            'category': tag_data['category'],
            'csrf_token': csrf_token
        }
        response = logged_in_admin.post(
            url_for('admin.tag.edit', id=new_tag.id),
            data=updated_data,
            follow_redirects=True
        )
        
        assert response.status_code == 200
        tags = get_all_tags()
        assert any(tag.name == tag_data['name'] and tag.category == tag_data['category'] for tag in tags)
        assert FLASH_MESSAGES["UPDATE_TAG_SUCCESS"].encode() in response.data

def test_update_tag_with_invalid_form_data(logged_in_admin, tag_data, db_session):
    with logged_in_admin.application.app_context():
        # Create a tag to update
        new_tag = create_tag(tag_data)
        db_session.commit()

        updated_data = {
            'name': '',  # Invalid name
            'csrf_token': extract_csrf_token(logged_in_admin.get(url_for('admin.tag.edit', id=new_tag.id)).data)
        }
        response = logged_in_admin.post(
            url_for('admin.tag.edit', id=new_tag.id),
            data=updated_data,
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["GENERIC_ERROR"].encode() in response.data

def test_update_tag_with_integrity_error(logged_in_admin, tag_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        # Create a tag to update
        new_tag = create_tag(tag_data)
        db_session.commit()

        def mock_commit(*args, **kwargs):
            raise IntegrityError("test", {}, None)

        monkeypatch.setattr(db_session, 'commit', mock_commit)

        update_response = logged_in_admin.get(url_for('admin.tag.edit', id=new_tag.id))
        assert update_response.status_code == 200

        csrf_token = extract_csrf_token(update_response.data)
        updated_data = {
            'name': new_tag.name,
            'csrf_token': csrf_token
        }
        response = logged_in_admin.post(
            url_for('admin.tag.edit', id=new_tag.id),
            data=updated_data,
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["UPDATE_TAG_ERROR"].encode() in response.data
