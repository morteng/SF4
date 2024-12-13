import pytest
from flask import url_for, get_flashed_messages
from app.models.user import User
from tests.conftest import extract_csrf_token
from app.forms.admin_forms import UserForm  # Added this line

@pytest.fixture(scope='function')
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepassword'
    }

@pytest.fixture(scope='function')
def test_user(db_session, user_data):
    user = User(**user_data)
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
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.user.create'))
        csrf_token = extract_csrf_token(response.data)

        response = logged_in_admin.post(url_for('admin.user.create'), data={
            'username': user_data['username'],
            'email': user_data['email'],
            'password': user_data['password'],
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200
        new_user = db_session.query(User).filter_by(username=user_data['username']).first()
        assert new_user is not None

def test_create_user_route_with_invalid_data(logged_in_admin, user_data):
    with logged_in_admin.application.app_context():
        invalid_data = {
            'username': '',  # Intentionally empty
            'email': user_data['email'],
            'password': user_data['password'],
            'csrf_token': extract_csrf_token(logged_in_admin.get(url_for('admin.user.create')).data)
        }
        
        response = logged_in_admin.post(url_for('admin.user.create'), data=invalid_data, follow_redirects=True)
        
        assert response.status_code == 200

        form = UserForm(data=invalid_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
            
        # Check that the user was not created
        new_user = db_session.query(User).filter_by(username=invalid_data['username']).first()
        assert new_user is None

def test_delete_user_route(logged_in_admin, test_user, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.user.delete', id=test_user.id))
        
        assert response.status_code == 302
        flash_message = list(filter(lambda x: 'deleted' in x, get_flashed_messages()))
        assert len(flash_message) > 0

        # Ensure the user is no longer in the session after deleting
        db_session.expire_all()
        updated_user = db_session.get(User, test_user.id)
        assert updated_user is None

def test_delete_nonexistent_user_route(logged_in_admin):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.user.delete', id=9999))
        
        assert response.status_code == 302
        flash_message = list(filter(lambda x: 'not found' in x, get_flashed_messages()))
        assert len(flash_message) > 0

def test_update_user_route(logged_in_admin, test_user, db_session):
    with logged_in_admin.application.app_context():
        update_response = logged_in_admin.get(url_for('admin.user.update', id=test_user.id))
        assert update_response.status_code == 200

        csrf_token = extract_csrf_token(update_response.data)
        updated_data = {
            'username': 'UpdatedUsername',
            'email': test_user.email,
            'password': test_user.password,
            'csrf_token': csrf_token
        }
        response = logged_in_admin.post(url_for('admin.user.update', id=test_user.id), data=updated_data, follow_redirects=True)

        assert response.status_code == 200
        updated_user = db_session.get(User, test_user.id)
        assert updated_user.username == 'UpdatedUsername'

def test_create_user_route_with_duplicate_username(logged_in_admin, test_user, user_data):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.user.create'))
        assert response.status_code == 200

        csrf_token = extract_csrf_token(response.data)
        duplicate_data = {
            'username': test_user.username,
            'email': "duplicate@example.com",
            'password': "anothersecurepassword",
            'csrf_token': csrf_token
        }
        response = logged_in_admin.post(url_for('admin.user.create'), data=duplicate_data, follow_redirects=True)

        assert response.status_code == 200
        form = UserForm(data=duplicate_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
    
        # Check that the user was not created
        new_user = db_session.query(User).filter_by(username=duplicate_data['username']).first()
        assert new_user.id == test_user.id  # Ensure it's the same user

def test_create_user_route_with_csrf_token(logged_in_admin, user_data):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.user.create'))
        assert response.status_code == 200
        csrf_token = extract_csrf_token(response.data)
        assert csrf_token is not None
