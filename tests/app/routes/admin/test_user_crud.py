import pytest
from flask import url_for
from app.models.user import User
from app.forms.admin_forms import UserForm
from tests.conftest import logged_in_admin, db_session, admin_user
import re

def extract_csrf_token(response_data):
    csrf_match = re.search(r'name="csrf_token" type="hidden" value="(.+?)"', response_data.decode('utf-8'))
    return csrf_match.group(1) if csrf_match else None

def test_create_user(logged_in_admin, db_session):
    response = logged_in_admin.get(url_for('admin.user.create'))
    csrf_token = extract_csrf_token(response.data)

    user_data = {
        'username': 'new_user',
        'email': 'new_user@example.com',
        'password': 'password123',
        'is_admin': True,
        'csrf_token': csrf_token
    }

    response = logged_in_admin.post(url_for('admin.user.create'), data=user_data)
    assert response.status_code == 302
    assert url_for('admin.user.index', _external=False) == response.headers['Location']

    new_user = db_session.query(User).filter_by(username='new_user').first()
    assert new_user is not None
    assert new_user.email == 'new_user@example.com'

def test_update_user(logged_in_admin, admin_user, db_session):
    response = logged_in_admin.get(url_for('admin.user.update', id=admin_user.id))
    csrf_token = extract_csrf_token(response.data)

    updated_data = {
        'username': 'updated_admin',
        'email': 'updated_admin@example.com',
        'is_admin': True,
        'csrf_token': csrf_token
    }

    response = logged_in_admin.post(url_for('admin.user.update', id=admin_user.id), data=updated_data)
    assert response.status_code == 302

    db_session.expire_all()
    user = db_session.query(User).get(admin_user.id)
    assert user.username == 'updated_admin'
    assert user.email == 'updated_admin@example.com'

def test_delete_user(logged_in_admin, admin_user, db_session):
    response = logged_in_admin.post(url_for('admin.user.delete', id=admin_user.id))
    assert response.status_code == 302

    deleted_user = db_session.query(User).get(admin_user.id)
    assert deleted_user is None

def test_index_users(logged_in_admin, admin_user):
    response = logged_in_admin.get(url_for('admin.user.index'))
    assert response.status_code == 200
    assert b'admin@example.com' in response.data
