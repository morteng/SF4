import pytest
from flask import url_for

@pytest.mark.csrf
def test_csrf_protection(client):
    """Test CSRF protection on protected routes"""
    # Try to access protected route without CSRF token
    response = client.post(url_for('public.login'), data={})
    assert response.status_code == 400
    assert b"CSRF token is missing" in response.data

@pytest.mark.csrf
def test_csrf_token_generation(client):
    """Test CSRF token generation"""
    response = client.get(url_for('public.login'))
    assert response.status_code == 200
    assert b'csrf_token' in response.data

@pytest.mark.csrf
def test_csrf_token_validation(client, db_session, app):
    """Test CSRF token validation"""
    # Create test user
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db_session.add(user)
        db_session.commit()

    # Get valid CSRF token
    response = client.get(url_for('public.login'))
    csrf_token = extract_csrf_token(response.data)
    
    # Test with valid token
    valid_response = client.post(url_for('public.login'), data={
        'username': 'testuser',
        'password': 'testpass',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert valid_response.status_code == 200
    
    # Test with invalid token
    invalid_response = client.post(url_for('public.login'), data={
        'username': 'testuser',
        'password': 'testpass',
        'csrf_token': 'invalid_token'
    }, follow_redirects=True)
    assert invalid_response.status_code == 400
