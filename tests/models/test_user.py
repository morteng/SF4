import pytest
from app.models.user import User
from datetime import datetime
from datetime import timezone

def test_user_creation(db_session):
    """Test basic user creation"""
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpass')
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('testpass')
    assert not user.check_password('wrongpass')

def test_user_password_hashing(db_session):
    """Test password hashing functionality"""
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpass')
    db_session.add(user)
    db_session.commit()
    
    assert user.password_hash is not None
    assert user.password_hash != 'testpass'
    assert user.check_password('testpass')
    assert not user.check_password('wrongpass')

def test_user_duplicate_username(db_session):
    """Test duplicate username constraint"""
    user1 = User(username='testuser', email='test1@example.com')
    user1.set_password('testpass')
    db_session.add(user1)
    db_session.commit()
    
    user2 = User(username='testuser', email='test2@example.com')
    user2.set_password('testpass')
    db_session.add(user2)
    
    with pytest.raises(Exception):
        db_session.commit()

def test_user_duplicate_email(db_session):
    """Test duplicate email constraint"""
    user1 = User(username='testuser1', email='test@example.com')
    user1.set_password('testpass')
    db_session.add(user1)
    db_session.commit()
    
    user2 = User(username='testuser2', email='test@example.com')
    user2.set_password('testpass')
    db_session.add(user2)
    
    with pytest.raises(Exception):
        db_session.commit()
