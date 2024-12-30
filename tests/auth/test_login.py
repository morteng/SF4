import pytest
from flask import url_for
from app.models.user import User
from tests.conftest import extract_csrf_token

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
    assert b"Hey! Welcome to our website." in response.data
    assert b"We hope you find everything you need here." in response.data

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
    
    assert b"The CSRF session token is missing" in response.data

def test_login_missing_csrf(client, test_user):
    """Test login with missing CSRF token"""
    response = client.post(url_for('public.login'), data={
        'username': test_user.username,
        'password': 'password123'
    }, follow_redirects=True)
    
    assert b"CSRF token is missing" in response.data

def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    login_response = client.get(url_for('public.login'))
    csrf_token = extract_csrf_token(login_response.data)
    
    response = client.post(url_for('public.login'), data={
        'username': test_user.username,
        'password': 'wrongpassword',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid username or password" in response.data

def test_login_empty_fields(client, db_session, app):
    """Test login with empty fields"""
    # Create test user
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db_session.add(user)
        db_session.commit()

    # Get CSRF token
    login_page = client.get(url_for('public.login'))
    csrf_token = extract_csrf_token(login_page.data)
    
    # Submit login with empty fields
    response = client.post(url_for('public.login'), data={
        'username': '',
        'password': '',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert b"This field is required" in response.data

def test_logout(client, logged_in_client):
    """Test logout functionality"""
    response = client.get(url_for('public.logout'), follow_redirects=True)
    assert response.status_code == 200
    assert b"Logged out successfully" in response.data
    with client.session_transaction() as session:
        assert '_user_id' not in session
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
    }, follow_redirects=True)

    # Verify response and session
    assert response.status_code == 200
    assert b"Login successful" in response.data
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
