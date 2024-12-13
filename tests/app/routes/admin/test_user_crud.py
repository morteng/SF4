import pytest
from flask import url_for
from app.models.user import User
from tests.conftest import extract_csrf_token

@pytest.fixture(scope='function')
def user_data():
    return {
        'username': 'testuser',
        'password': 'password123',
        'email': 'testuser@example.com'
    }

@pytest.fixture(scope='function')
def test_user(db_session, user_data):
    user = User(
        username=user_data['username'],
        password=user_data['password'],
        email=user_data['email']
    )
    db_session.add(user)
    db_session.commit()
    yield user

    # Teardown: Attempt to delete the user and rollback if an error occurs
    try:
        db_session.delete(user)
        db_session.commit()
    except Exception as e:
        print(f"Failed to delete test user during teardown: {e}")
        db_session.rollback()

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
    assert not any(user.username == '' for user in users)  # Ensure no user with an empty username was created

def test_update_user_route(logged_in_admin, test_user, db_session):
    update_response = logged_in_admin.get(url_for('admin.user.update', id=test_user.id))
    assert update_response.status_code == 200

    csrf_token = extract_csrf_token(update_response.data)
    updated_data = {
        'username': 'updateduser',
        'password': test_user.password,
        'email': test_user.email,
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.user.update', id=test_user.id), data=updated_data, follow_redirects=True)

    assert response.status_code == 200
    updated_user = db_session.get(User, test_user.id)  # Use db_session.get to retrieve the user
    assert updated_user.username == 'updateduser'

def test_update_user_route_with_invalid_id(logged_in_admin):
    update_response = logged_in_admin.get(url_for('admin.user.update', id=9999))
    assert update_response.status_code == 302
    assert url_for('admin.user.index', _external=False) == update_response.headers['Location']

def test_delete_user_route(logged_in_admin, test_user, db_session):
    # Perform the DELETE operation
    delete_response = logged_in_admin.post(url_for('admin.user.delete', id=test_user.id))
    assert delete_response.status_code == 302
    
    # Ensure the user is no longer in the session after deleting
    db_session.expire_all()
    updated_user = db_session.get(User, test_user.id)
    assert updated_user is None

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
        assert b"Failed to create user." in response.data  # Confirm error message is present

        users = User.query.all()
        assert not any(user.username == data['username'] for user in users)  # Ensure no user was created

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
            'password': test_user.password,
            'email': test_user.email,
            'csrf_token': csrf_token
        }
        response = logged_in_admin.post(url_for('admin.user.update', id=test_user.id), data=updated_data, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"Failed to update user." in response.data  # Confirm error message is present

        updated_user = db_session.get(User, test_user.id)  # Use db_session.get to retrieve the user
        assert updated_user.username != 'updateduser'
