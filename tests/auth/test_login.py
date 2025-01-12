import pytest
from flask import url_for, get_flashed_messages
from app.models.user import User
from tests.conftest import extract_csrf_token

@pytest.fixture(scope='function')
def test_user(db_session):
    """Fixture providing a test user"""
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.delete(user)
    db_session.commit()

def test_login_page_loads(client):
    """Test that login page loads successfully"""
    response = client.get(url_for('public.login'))
    assert response.status_code == 200
    assert b"Login" in response.data

def test_login_success(client, test_user):
    """Test successful login flow"""
    # Get CSRF token
    login_response = client.get(url_for('public.login'))
    csrf_token = extract_csrf_token(login_response.data)
    
    # Submit valid login
    response = client.post(url_for('public.login'), data={
        'username': test_user.username,
        'password': 'password123',
        'csrf_token': csrf_token
    })

    # Verify redirect to admin dashboard
    assert response.status_code == 302
    assert response.location == url_for('admin.dashboard')
    
    # Verify session contains user_id
    with client.session_transaction() as session:
        assert '_user_id' in session
        assert session['_user_id'] == str(test_user.id)

def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    # Get CSRF token
    login_response = client.get(url_for('public.login'))
    csrf_token = extract_csrf_token(login_response.data)
    
    # Submit invalid login
    response = client.post(url_for('public.login'), data={
        'username': test_user.username,
        'password': 'wrongpassword',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    # Verify error message and session
    assert response.status_code == 200
    messages = get_flashed_messages()
    assert "Invalid username or password" in messages
    with client.session_transaction() as session:
        assert '_user_id' not in session

def test_login_missing_fields(client):
    """Test login with missing required fields"""
    # Get CSRF token
    login_response = client.get(url_for('public.login'))
    csrf_token = extract_csrf_token(login_response.data)
    
    # Submit empty form
    response = client.post(url_for('public.login'), data={
        'username': '',
        'password': '',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    # Verify validation errors
    assert response.status_code == 200
    assert b"This field is required" in response.data

def test_login_inactive_user(client, db_session):
    """Test login attempt with inactive user"""
    # Create inactive user
    user = User(username='inactive', email='inactive@example.com', is_active=False)
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Get CSRF token
    login_response = client.get(url_for('public.login'))
    csrf_token = extract_csrf_token(login_response.data)
    
    # Submit login
    response = client.post(url_for('public.login'), data={
        'username': 'inactive',
        'password': 'password123',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    # Verify error message
    assert response.status_code == 200
    messages = get_flashed_messages()
    assert "Your account is inactive" in messages
    with client.session_transaction() as session:
        assert '_user_id' not in session

def test_login_already_authenticated(client, logged_in_client):
    """Test login attempt when already authenticated"""
    response = client.get(url_for('public.login'), follow_redirects=True)
    assert response.status_code == 200
    assert b"already logged in" in response.data
