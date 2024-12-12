import pytest
from app.models.user import User
from app.services.user_service import create_user, delete_user, get_user_by_id, get_all_users

def test_create_user(db_session):
    user_data = {'username': 'test_user', 'email': 'test_user@example.com', 'password': 'password123'}
    user = create_user(user_data)
    assert user.username == 'test_user'
    assert user.email == 'test_user@example.com'

    db_session.expire_all()
    saved_user = db_session.query(User).filter_by(email='test_user@example.com').first()
    assert saved_user is not None

def test_create_user_duplicate_email(db_session):
    user_data = {'username': 'duplicate_user', 'email': 'admin@example.com', 'password': 'password123'}
    with pytest.raises(ValueError):
        create_user(user_data)

def test_get_user_by_id(db_session, admin_user):
    user = get_user_by_id(admin_user.id)
    assert user is not None
    assert user.username == admin_user.username

def test_get_all_users(db_session, admin_user):
    users = get_all_users()
    assert len(users) >= 1
    assert admin_user in users

def test_delete_user(db_session, admin_user):
    delete_user(admin_user)
    db_session.expire_all()
    user = db_session.query(User).get(admin_user.id)
    assert user is None
