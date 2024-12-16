from flask import url_for
from app.models.user import User
from tests.conftest import logged_in_admin, user_data, extract_csrf_token
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR

def test_create_user_route(logged_in_admin, user_data):
    create_response = logged_in_admin.get(url_for('admin.user.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    response = logged_in_admin.post(url_for('admin.user.create'), data={
        'username': user_data['username'],
        'password': user_data['password'],
        'email': user_data['email'],
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    users = User.query.all()
    assert any(user.username == user_data['username'] and user.email == user_data['email'] for user in users)
    assert FLASH_MESSAGES["CREATE_USER_SUCCESS"].encode() in response.data

def test_create_user_route_with_invalid_data(logged_in_admin, user_data):
    create_response = logged_in_admin.get(url_for('admin.user.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    invalid_data = {
        'username': '',  # Invalid username
        'password': user_data['password'],
        'email': user_data['email'],
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.user.create'), data=invalid_data, follow_redirects=True)

    assert response.status_code == 200
    users = User.query.all()
    assert not any(user.username == '' for user in users)
    assert FLASH_MESSAGES["CREATE_USER_ERROR"].encode() in response.data

def test_update_user_route(logged_in_admin, test_user, db_session):
    update_response = logged_in_admin.get(url_for('admin.user.update', id=test_user.id))
    assert update_response.status_code == 200

    csrf_token = extract_csrf_token(update_response.data)
    updated_data = {
        'username': 'updateduser',
        'password': 'newpassword123',
        'email': test_user.email,
        'is_admin': False,
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.user.update', id=test_user.id), data=updated_data, follow_redirects=True)

    assert response.status_code == 200
    updated_user = db_session.get(User, test_user.id)
    assert updated_user.username == 'updateduser'
    assert updated_user.check_password('newpassword123')
    assert FLASH_MESSAGES["UPDATE_USER_SUCCESS"].encode() in response.data

def test_update_user_with_database_error(logged_in_admin, test_user, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        update_response = logged_in_admin.get(url_for('admin.user.update', id=test_user.id))
        assert update_response.status_code == 200

        csrf_token = extract_csrf_token(update_response.data)
        updated_data = {
            'username': 'updateduser',
            'password': 'newpassword123',
            'email': test_user.email,
            'csrf_token': csrf_token
        }
        response = logged_in_admin.post(url_for('admin.user.update', id=test_user.id), data=updated_data, follow_redirects=True)
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["UPDATE_USER_ERROR"].encode() in response.data

def test_create_user_route_with_database_error(logged_in_admin, user_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        data = user_data

        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.user.create'), data=data, follow_redirects=True)
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["CREATE_USER_ERROR"].encode() in response.data

def test_delete_user_route(logged_in_admin, test_user, db_session):
    delete_response = logged_in_admin.post(url_for('admin.user.delete', id=test_user.id))
    assert delete_response.status_code == 302
    
    db_session.expire_all()
    updated_user = db_session.get(User, test_user.id)
    assert updated_user is None
    # Assuming the flash message is flashed after redirect
    # You might need to check the session or use a different method to verify this

def test_delete_user_route_with_invalid_id(logged_in_admin):
    delete_response = logged_in_admin.post(url_for('admin.user.delete', id=9999))
    assert delete_response.status_code == 302
    # Assuming the flash message is flashed after redirect
    # You might need to check the session or use a different method to verify this
