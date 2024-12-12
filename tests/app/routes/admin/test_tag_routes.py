import pytest
from flask import url_for
from app.models.tag import Tag
from app.services.tag_service import get_all_tags, delete_tag, create_tag, get_tag_by_id, update_tag
from sqlalchemy.exc import SQLAlchemyError
from tests.conftest import extract_csrf_token

@pytest.fixture(scope='function')
def tag_data():
    """Provide test data for tags."""
    return {
        'name': 'Test Tag',
        'category': 'TestCategory'
    }

@pytest.fixture(scope='function')
def test_tag(db_session, tag_data):
    """Provide a test tag for use in tests."""
    tag = Tag(
        name=tag_data['name'],
        category=tag_data['category']
    )
    db_session.add(tag)
    db_session.commit()
    yield tag

    # Teardown: Attempt to delete the tag and rollback if an error occurs
    try:
        db_session.delete(tag)
        db_session.commit()
    except SQLAlchemyError as e:
        print(f"Failed to delete test tag during teardown: {e}")
        db_session.rollback()

@pytest.fixture(scope='function')
def another_test_tag(db_session, tag_data):
    """Provide another test tag for use in tests."""
    another_tag = Tag(
        name='Another Test Tag',
        category=tag_data['category']
    )
    db_session.add(another_tag)
    db_session.commit()
    yield another_tag

    # Teardown: Attempt to delete the tag and rollback if an error occurs
    try:
        db_session.delete(another_tag)
        db_session.commit()
    except SQLAlchemyError as e:
        print(f"Failed to delete test tag during teardown: {e}")
        db_session.rollback()

@pytest.fixture(scope='function')
def logged_in_admin(client, admin_user):
    login_response = client.get(url_for('public.login'))  # Fetch the login page to get CSRF token
    csrf_token = extract_csrf_token(login_response.data)
    
    response = client.post(url_for('public.login'), data={
        'username': admin_user.username,
        'password': 'password123',
        'csrf_token': csrf_token  # Use the extracted CSRF token
    }, follow_redirects=True)
    assert response.status_code == 200, "Admin login failed."
    with client.session_transaction() as session:
        assert '_user_id' in session, "Admin session not established."
    yield client

def test_create_tag_route(logged_in_admin, tag_data):
    create_response = logged_in_admin.get(url_for('admin.tag.create'))  # Updated line
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    response = logged_in_admin.post(url_for('admin.tag.create'), data={
        'name': tag_data['name'],
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    tags = get_all_tags()
    assert any(tag.name == tag_data['name'] for tag in tags)

def test_index_tag_route(logged_in_admin, test_tag):
    index_response = logged_in_admin.get(url_for('admin.tag.index'))
    assert index_response.status_code == 200

def test_delete_tag_route(logged_in_admin, test_tag):
    delete_response = logged_in_admin.post(url_for('admin.tag.delete', id=test_tag.id))
    assert delete_response.status_code == 302
    tags = get_all_tags()
    assert not any(tag.id == test_tag.id for tag in tags)

def test_update_tag_route(logged_in_admin, test_tag, another_test_tag):
    update_response = logged_in_admin.get(url_for('admin.tag.update', id=test_tag.id))
    assert update_response.status_code == 200

    csrf_token = extract_csrf_token(update_response.data)
    updated_data = {
        'name': another_test_tag.name,
        'category': 'UpdatedCategory',
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.tag.update', id=test_tag.id), data=updated_data, follow_redirects=True)

    assert response.status_code == 200
    updated_tag = get_tag_by_id(test_tag.id)
    assert updated_tag.name == updated_data['name']
    assert updated_tag.category == updated_data['category']

def test_get_tag_by_id_route(logged_in_admin, test_tag):
    index_response = logged_in_admin.get(url_for('admin.tag.index'))
    assert index_response.status_code == 200

    update_response = logged_in_admin.get(url_for('admin.tag.update', id=test_tag.id))
    assert update_response.status_code == 200
