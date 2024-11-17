import pytest
from app.models.user import User

def test_set_password():
    user = User(username='testuser')
    user.set_password('testpassword')
    assert user.password_hash is not None
    assert user.check_password('testpassword') is True

def test_check_password():
    user = User(username='testuser')
    user.set_password('testpassword')
    assert user.check_password('wrongpassword') is False
