import pytest
from flask import url_for
from app.models.user import User

def test_login(client, db_session, app):
    """Test login flow including CSRF protection"""
    # Create test user
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db_session.add(user)
        db_session.commit()

    # Get login page and extract CSRF token
    login_page = client.get(url_for('public.login'))
    assert login_page.status_code == 200
    
    csrf_token = extract_csrf_token(login_page.data)
    assert csrf_token is not None, "CSRF token not found in login form"
    
    # Submit login with valid credentials and CSRF token
    response = client.post(url_for('public.login'), data={
        'username': 'testuser',
        'password': 'testpass',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Login successful" in response.data

def test_login_invalid_csrf(client, db_session, app):
    """Test login with invalid CSRF token"""
    # Create test user
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db_session.add(user)
        db_session.commit()

    # Submit login with invalid CSRF token
    response = client.post(url_for('public.login'), data={
        'username': 'testuser',
        'password': 'testpass',
        'csrf_token': 'invalid_token'
    }, follow_redirects=True)
    
    assert b"CSRF token is invalid" in response.data

def test_login_missing_csrf(client, db_session, app):
    """Test login with missing CSRF token"""
    # Create test user
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db_session.add(user)
        db_session.commit()

    # Submit login without CSRF token
    response = client.post(url_for('public.login'), data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    
    assert b"CSRF token is missing" in response.data
