import pytest
from flask import url_for
from app.models.user import User
from tests.conftest import extract_csrf_token, logged_in_admin
from app.constants import FlashMessages, FlashCategory
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='function')
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }

@pytest.fixture(scope='function')
def test_user(db_session, user_data):
    """Provide a test user."""
    user = User(
        username=user_data['username'],
        email=user_data['email'],
        password_hash=generate_password_hash(user_data['password']),
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.delete(user)
    db_session.commit()

def test_create_user_route(logged_in_admin, user_data):
    create_response = logged_in_admin.get(url_for('admin.user.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    response = logged_in_admin.post(url_for('admin.user.create'), data={
        'username': user_data['username'],
        'email': user_data['email'],
        'password': user_data['password'],
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    users = User.query.all()
    assert any(user.username == user_data['username'] and user.email == user_data['email'] for user in users)
    # Assert the flash message using constants
    assert FlashMessages.CREATE_USER_SUCCESS.encode() in response.data

def test_create_user_route_with_invalid_data(logged_in_admin, user_data):
    create_response = logged_in_admin.get(url_for('admin.user.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    invalid_data = {
        'username': '',  # Invalid username
        'email': user_data['email'],
        'password': user_data['password'],
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.user.create'), data=invalid_data, follow_redirects=True)

    assert response.status_code == 200
    users = User.query.all()
    assert not any(user.username == '' for user in users)  # Ensure no user with an empty username was created
    # Assert the flash message using constants
    assert FlashMessages.CREATE_USER_INVALID_DATA.encode() in response.data

def test_update_user_route(logged_in_admin, test_user, db_session):
    update_response = logged_in_admin.get(url_for('admin.user.edit', id=test_user.id))
    assert update_response.status_code == 200

    csrf_token = extract_csrf_token(update_response.data)
    updated_data = {
        'username': 'updateduser',
        'email': test_user.email,
        'password': test_user.password_hash,  # Assuming password hash is not changed in this test
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.user.edit', id=test_user.id), data=updated_data, follow_redirects=True)

    assert response.status_code == 200
    updated_user = db_session.get(User, test_user.id)
    assert updated_user.username == 'updateduser'
    # Assert the flash message using constants
    assert FlashMessages.UPDATE_USER_SUCCESS.encode() in response.data

def test_update_user_route_with_invalid_id(logged_in_admin):
    update_response = logged_in_admin.get(url_for('admin.user.edit', id=9999))
    assert update_response.status_code == 302
    assert url_for('admin.user.index', _external=False) == update_response.headers['Location']

def test_delete_user_route(logged_in_admin, test_user, db_session):
    # Perform the DELETE operation
    delete_response = logged_in_admin.post(
        url_for('admin.user.delete', id=test_user.id),
        follow_redirects=True  # Follow the redirect to capture flash messages
    )
    assert delete_response.status_code == 200  # After following redirects, status should be 200
    
    # Ensure the user is no longer in the session after deleting
    db_session.expire_all()
    updated_user = db_session.get(User, test_user.id)
    assert updated_user is None
    # Assert the flash message using constants
    assert FlashMessages.DELETE_USER_SUCCESS.encode() in delete_response.data

def test_delete_user_route_with_invalid_id(logged_in_admin):
    delete_response = logged_in_admin.post(url_for('admin.user.delete', id=9999))
    assert delete_response.status_code == 302
    assert url_for('admin.user.index', _external=False) == delete_response.headers['Location']

def test_create_user_route_with_database_error(logged_in_admin, user_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        data = user_data

        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.user.create'), data=data)
        
        assert response.status_code == 200
        # Assert the flash message using constants
        assert FlashMessages.CREATE_USER_ERROR.encode() in response.data

        users = User.query.all()
        assert not any(user.username == data['username'] for user in users)  # Ensure no user was created
