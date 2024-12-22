from flask import url_for
from app.models.tag import Tag
from tests.conftest import logged_in_admin, tag_data, extract_csrf_token, get_all_tags
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR

def test_create_tag_route(logged_in_admin, tag_data):
    create_response = logged_in_admin.get(url_for('admin.tag.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    response = logged_in_admin.post(url_for('admin.tag.create'), data={
        'name': tag_data['name'],
        'category': tag_data['category'],
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    tags = get_all_tags()  # Removed the app argument
    assert any(tag.name == tag_data['name'] and tag.category == tag_data['category'] for tag in tags)
    assert FLASH_MESSAGES["CREATE_TAG_SUCCESS"].encode() in response.data

def test_create_tag_route_with_none_result(logged_in_admin, tag_data, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_create_tag(*args, **kwargs):
            return None

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
        })

        assert response.status_code == 200
        assert FLASH_MESSAGES["CREATE_TAG_ERROR"].encode() in response.data

def test_create_tag_route_with_database_error(logged_in_admin, tag_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.tag.create'), data=tag_data)
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["CREATE_TAG_ERROR"].encode() in response.data

def test_update_tag_with_invalid_form_data(logged_in_admin, test_tag, tag_data, db_session):
    with logged_in_admin.application.app_context():
        # Merge the test_tag back into the session to ensure it's not detached
        test_tag = db_session.merge(test_tag)
        
        updated_data = {
            'name': '',
            'category': test_tag.category,
            'csrf_token': extract_csrf_token(logged_in_admin.get(url_for('admin.tag.edit', id=test_tag.id)).data)
        }
        response = logged_in_admin.post(
            url_for('admin.tag.edit', id=test_tag.id),
            data=updated_data
        )
        
        assert response.status_code == 200
        # Ensure the correct flash message is set
        assert FLASH_MESSAGES["GENERIC_ERROR"].encode() in response.data

def test_update_tag_with_database_error(logged_in_admin, test_tag, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        update_response = logged_in_admin.get(url_for('admin.tag.edit', id=test_tag.id))
        assert update_response.status_code == 200

        csrf_token = extract_csrf_token(update_response.data)
        updated_data = {
            'name': test_tag.name,
            'category': test_tag.category,
            'csrf_token': csrf_token
        }
        response = logged_in_admin.post(
            url_for('admin.tag.edit', id=test_tag.id),
            data=updated_data,
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["UPDATE_TAG_ERROR"].encode() in response.data
