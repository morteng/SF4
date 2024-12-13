import pytest
from flask import url_for, get_flashed_messages
from app.models.tag import Tag
from tests.conftest import extract_csrf_token
from app.forms.admin_forms import TagForm  # Added this line

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
    except Exception as e:
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
        'category': tag_data['category'],  # Added this line
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    tags = Tag.query.all()
    assert any(tag.name == tag_data['name'] and tag.category == tag_data['category'] for tag in tags)

def test_create_tag_route_with_invalid_data(logged_in_admin, tag_data):
    create_response = logged_in_admin.get(url_for('admin.tag.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    invalid_data = {
        'name': '',  # Intentionally empty
        'category': tag_data['category'],
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.tag.create'), data=invalid_data, follow_redirects=True)

    assert response.status_code == 200
    form = TagForm(data=invalid_data)
    if not form.validate():
        for field, errors in form.errors.items():
            print(f"Field {field} errors: {errors}")
    
    # Check that the tag was not created
    tags = Tag.query.all()
    assert not any(tag.name == '' and tag.category == tag_data['category'] for tag in tags)

def test_delete_tag_route(logged_in_admin, test_tag, db_session):
    delete_response = logged_in_admin.post(url_for('admin.tag.delete', id=test_tag.id))
    assert delete_response.status_code == 302
    flash_message = list(filter(lambda x: 'deleted' in x, get_flashed_messages()))
    assert len(flash_message) > 0

    # Ensure the tag is no longer in the session after deleting
    db_session.expire_all()
    updated_tag = db_session.get(Tag, test_tag.id)
    assert updated_tag is None

def test_delete_nonexistent_tag_route(logged_in_admin):
    delete_response = logged_in_admin.post(url_for('admin.tag.delete', id=9999))
    assert delete_response.status_code == 302
    flash_message = list(filter(lambda x: 'not found' in x, get_flashed_messages()))
    assert len(flash_message) > 0

def test_update_tag_route(logged_in_admin, test_tag, db_session):
    update_response = logged_in_admin.get(url_for('admin.tag.update', id=test_tag.id))
    assert update_response.status_code == 200

    csrf_token = extract_csrf_token(update_response.data)
    updated_data = {
        'name': 'Updated Tag Name',
        'category': test_tag.category,
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.tag.update', id=test_tag.id), data=updated_data, follow_redirects=True)

    assert response.status_code == 200
    updated_tag = db_session.get(Tag, test_tag.id)
    assert updated_tag.name == 'Updated Tag Name'

def test_create_tag_route_with_duplicate_name(logged_in_admin, test_tag, tag_data):
    create_response = logged_in_admin.get(url_for('admin.tag.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    duplicate_data = {
        'name': test_tag.name,
        'category': "DuplicateCategory",
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.tag.create'), data=duplicate_data, follow_redirects=True)

    assert response.status_code == 200
    form = TagForm(data=duplicate_data)
    if not form.validate():
        for field, errors in form.errors.items():
            print(f"Field {field} errors: {errors}")
    
    # Check that the tag was not created
    tags = Tag.query.all()
    assert len(tags) == 1  # Only the test_tag should exist

def test_create_tag_route_with_csrf_token(logged_in_admin, tag_data):
    create_response = logged_in_admin.get(url_for('admin.tag.create'))
    assert create_response.status_code == 200
    csrf_token = extract_csrf_token(create_response.data)
    assert csrf_token is not None
