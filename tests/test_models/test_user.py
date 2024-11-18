import pytest
from app.models.user import User

@pytest.fixture(scope='function')
def user():
    return User(username='testuser')

def test_set_password(user):
    user.set_password('testpassword')
    assert user.password_hash is not None
    assert user.check_password('testpassword') is True

def test_check_password(user):
    user.set_password('testpassword')
    assert user.check_password('wrongpassword') is False
