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



    # Get CSRF token
    login_page = client.get(url_for('public.login'))
    csrf_token = extract_csrf_token(login_page.data)
    
    # Submit login with invalid credentials
    response = client.post(url_for('public.login'), data={
        'username': 'wronguser',
        'password': 'wrongpass',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
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
from flask import url_for
from app.models.user import User
from tests.conftest import extract_csrf_token

@pytest.fixture(scope='function')
def test_user(db_session):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    yield user
    try:
        db_session.delete(user)
        db_session.commit()
    except Exception as e:
        print(f"Failed to delete test user during teardown: {e}")
        db_session.rollback()

def test_login_success(client, test_user):
    """Test successful login flow"""
    login_response = client.get(url_for('public.login'))
    assert login_response.status_code == 200

    csrf_token = extract_csrf_token(login_response.data)
    response = client.post(url_for('public.login'), data={
        'username': test_user.username,
        'password': 'password123',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    with client.session_transaction() as session:
        assert '_user_id' in session

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
    # Check for flashed message instead of HTML content
    assert b"Invalid username or password" in response.data
    # TODO: Properly verify error message display once we have access to templates
    with client.session_transaction() as session:
        assert '_user_id' not in session

def test_login_missing_fields(client, test_user):
    """Test login with missing required fields"""
    login_response = client.get(url_for('public.login'))
    csrf_token = extract_csrf_token(login_response.data)
    
    response = client.post(url_for('public.login'), data={
        'username': '',
        'password': '',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"This field is required" in response.data
