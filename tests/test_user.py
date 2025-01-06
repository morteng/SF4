import pytest
from flask import url_for, session

def test_login_redirect(client, test_user):
    """Test that login redirects to the correct page after successful authentication"""
    # Test data
    login_data = {
        'username': test_user.username,
        'password': 'TestPass123!'
    }
    
    # Make login request
    response = client.post(url_for('public.login'), data=login_data, follow_redirects=False)
    
    # Verify redirect status code and location
    assert response.status_code == 302
    assert response.location == url_for('public.index', _external=True)

def test_user_password_hashing(test_user):
    """Test password hashing functionality"""
    # Verify password hashing
    assert test_user.check_password('TestPass123!')
    assert not test_user.check_password('wrongpassword')

def test_user_creation(db_session, app):
    """Test user creation with all required fields"""
    with app.app_context():
        user = User(
            username='newuser',
            email='newuser@example.com',
            password='TestPass123!'
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.check_password('TestPass123!')

def test_login_success(client):
    """Test successful login sets session variables"""
    # Test data
    test_user = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    
    # Make login request with redirect following
    response = client.post(url_for('public.login'), data=test_user, follow_redirects=True)
    
    # Verify response and session
    assert response.status_code == 200
    assert 'user_id' in session
    assert 'username' in session
    assert session['username'] == test_user['username']

def test_login_failure(client):
    """Test failed login returns appropriate error"""
    # Test data with invalid credentials
    invalid_user = {
        'username': 'wronguser',
        'password': 'wrongpassword'
    }
    
    # Make login request
    response = client.post(url_for('public.login'), data=invalid_user, follow_redirects=True)
    
    # Verify response
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data
    assert 'user_id' not in session

def test_login_missing_fields(client):
    """Test login with missing required fields"""
    # Test data with missing password
    incomplete_user = {
        'username': 'testuser'
    }
    
    # Make login request
    response = client.post(url_for('public.login'), data=incomplete_user, follow_redirects=True)
    
    # Verify response
    assert response.status_code == 200
    assert b"This field is required" in response.data
    assert 'user_id' not in session
