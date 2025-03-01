import pytest
import time
from unittest.mock import patch
from flask import session, url_for, current_app, request
from flask_limiter import Limiter
from bs4 import BeautifulSoup
from werkzeug.security import generate_password_hash
from bs4 import BeautifulSoup

from app.forms.user_forms import ProfileForm, LoginForm
from app import create_app
from app.models.user import User
from app.models.audit_log import AuditLog
from app.extensions import db
from app.constants import FlashMessages, FlashCategory
from app.utils import generate_csrf_token, flash_message

@pytest.fixture(scope='function', autouse=True)
def setup_database(_db):
    """Ensure the User table exists before running tests."""
    try:
        _db.create_all()
        yield
    finally:
        _db.session.rollback()
        _db.drop_all()

@pytest.fixture(scope='function')
def app():
    app = create_app('testing')  # Ensures 'testing' config is loaded
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

def test_profile_form_valid(client, setup_database):
    """Test valid profile form submission"""
    # Create a test user
    password_hash = generate_password_hash("password123")
    user = User(username="testuser", email="test@example.com", password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    
    with client:
        # Get login page to establish session
        login_page = client.get(url_for('public.login'))
        assert login_page.status_code == 200
        
        # Extract CSRF token from login form
        soup = BeautifulSoup(login_page.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        assert csrf_token, "CSRF token not found in login form"
        
        # Login the user
        login_response = client.post(url_for('public.login'), data={
            'username': 'testuser',
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert login_response.status_code == 200, "Login failed"

        # Clear audit logs from login operation
        AuditLog.query.delete()
        db.session.commit()

        # Get profile edit page
        profile_page = client.get(url_for('user.edit_profile'))
        assert profile_page.status_code == 200
        
        # Extract CSRF token from profile form
        soup = BeautifulSoup(profile_page.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        assert csrf_token, "CSRF token not found in profile form"
        
        # Submit profile update
        response = client.post(url_for('user.edit_profile'), data={
            'username': 'newusername',
            'email': 'newemail@example.com',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        # Verify response
        assert response.status_code == 200
        assert FlashMessages.PROFILE_UPDATE_SUCCESS.value.encode() in response.data
        
        # Verify user was updated
        updated_user = User.query.get(user.id)
        assert updated_user.username == 'newusername'
        assert updated_user.email == 'newemail@example.com'
        
        # Verify audit log was created
        audit_log = AuditLog.query.filter_by(user_id=user.id).first()
        assert audit_log is not None
        assert audit_log.action == "profile_update"
        assert "newusername" in audit_log.details
        assert "newemail@example.com" in audit_log.details

def test_profile_form_invalid_same_username(client, setup_database):
    # Increase rate limit for testing
    current_app.config['RATELIMIT_DEFAULT'] = "10 per minute"
    
    # Create existing user
    password_hash = generate_password_hash("password123")
    user = User(username="existinguser", email="existing@example.com", password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    # Create and log in as test user
    test_user = User(
        username="testuser", 
        email="test@example.com", 
        password_hash=password_hash
    )
    db.session.add(test_user)
    db.session.commit()
    
    # Log in the user
    with client:
        # Only reset limiter if rate limiting is enabled and initialized
        if current_app.config.get('RATELIMIT_ENABLED', True):
            limiter = current_app.extensions.get('limiter')
            if limiter and limiter._storage:  # Check if limiter is properly initialized
                limiter.reset()
        
        # First make a GET request to establish session and get CSRF token
        get_response = client.get(url_for('public.login'))
        assert get_response.status_code == 200
            
        # Extract CSRF token using BeautifulSoup
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

        # Only reset limiter if rate limiting is enabled and initialized
        if current_app.config.get('RATELIMIT_ENABLED', True):
            limiter = current_app.extensions.get('limiter')
            if limiter and limiter._storage:  # Check if limiter is properly initialized
                limiter.reset()
            
        # Now make the login POST request
        login_response = client.post(url_for('public.login'), data={
            'username': 'testuser',
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert login_response.status_code == 200, "Login failed"
        
        # Only reset limiter if rate limiting is enabled and initialized
        if current_app.config.get('RATELIMIT_ENABLED', True):
            limiter = current_app.extensions.get('limiter')
            if limiter and limiter._storage:  # Check if limiter is properly initialized
                limiter.reset()
        
        # Get CSRF token from the profile edit page
        get_response = client.get('/user/profile/edit')
        assert get_response.status_code == 200, "Failed to access profile edit page"
    soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    assert csrf_token, "CSRF token not found in form"

    # Verify form data is valid
    with client.application.test_request_context():
        form = ProfileForm(
            username='existinguser',
            email='newemail@example.com',
            csrf_token=csrf_token,
            original_username='testuser',
            original_email='test@example.com'
        )
        assert not form.validate(), "Form should be invalid with duplicate username"
        assert FlashMessages.USERNAME_ALREADY_EXISTS.value in form.username.errors, \
            "Expected username validation error not found"

    # Test form submission with duplicate username
    response = client.post('/user/profile/edit', data={
        'username': 'existinguser',
        'email': 'newemail@example.com',
        'csrf_token': csrf_token
    }, follow_redirects=True)
        
    # Debugging: Print response data if status is not 200
    if response.status_code != 200:
        print("Response data:", response.data.decode())
        
    # Verify the response status code and error message
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert FlashMessages.USERNAME_ALREADY_EXISTS.value.encode() in response.data, \
        "Expected username validation error not found in response"

    # Log out and clean up
    client.get('/logout')
    db.session.delete(user)
    db.session.delete(test_user)
    db.session.commit()

def test_profile_form_invalid_same_email(client, setup_database):
    # Clean up any existing test users
    User.query.filter_by(email="existing@example.com").delete()
    db.session.commit()
    
    # Add a test user with a unique email
    password_hash = generate_password_hash("password123")
    user = User(username="existinguser", email="existing@example.com", password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    # Create and log in as test user
    test_user = User(
        username="testuser", 
        email="test@example.com", 
        password_hash=password_hash
    )
    db.session.add(test_user)
    db.session.commit()
    
    # Log in the user
    with client:
        # First make a GET request to establish session and get CSRF token
        get_response = client.get(url_for('public.login'))
        assert get_response.status_code == 200
            
        # Extract CSRF token using BeautifulSoup
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

        # Now make the login POST request
        login_response = client.post(url_for('public.login'), data={
            'username': 'testuser',
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert login_response.status_code == 200, "Login failed"

        with client.application.test_request_context():
            form = ProfileForm(
                original_username="testuser", 
                original_email="test@example.com"
            )
            form.username.data = "newusername"
            form.email.data = "existing@example.com"
            assert not form.validate()
            assert FlashMessages.EMAIL_ALREADY_EXISTS.value in form.email.errors

            # Test with invalid email format
            form.email.data = "invalid-email"
            assert not form.validate()
            assert "Invalid email address." in form.email.errors

    # Clean up after the test
    User.query.filter_by(email="existing@example.com").delete()
    db.session.delete(test_user)
    db.session.commit()

def test_login_form_valid(client, setup_database):
    # Create test user in database
    password_hash = generate_password_hash("password123")
    user = User(username="testuser", email="test@example.com", password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    # First make a GET request to establish session and get CSRF token
    get_response = client.get(url_for('public.login'))
    assert get_response.status_code == 200

    # Extract CSRF token using BeautifulSoup
    soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    assert csrf_token, "CSRF token not found in form"

    # Test form submission with the correct CSRF token
    response = client.post(url_for('public.login'), data={
        'username': 'testuser',
        'password': 'password123',
        'csrf_token': csrf_token
    }, follow_redirects=False)  # Don't follow redirects to verify status code

    # Verify the response status code
    assert response.status_code == 302, f"Expected 302, got {response.status_code}"

    # Clean up
    db.session.delete(user)
    db.session.commit()

def test_login_form_invalid_missing_username(client):
    with client.application.test_request_context():  # Added request context
        # Test form validation with CSRF token
        form = LoginForm(csrf_token=generate_csrf_token())
        form.password.data = "password123"
        assert form.validate() == False
        assert 'This field is required.' in form.username.errors

        # Test form submission via POST
        response = client.post(url_for('public.login'), data={
            'password': 'password123',
            'csrf_token': generate_csrf_token()
        })
        assert response.status_code == 400  # Expect 400 for validation errors

def test_login_form_invalid_missing_password(client):
    with client.application.test_request_context():  # Added request context
        form = LoginForm()
        form.username.data = "testuser"
        assert form.validate() == False
        assert 'This field is required.' in form.password.errors
def test_profile_form_invalid_csrf_token(client, setup_database):
    """Test profile form submission with invalid CSRF token"""
    # Create test user
    password_hash = generate_password_hash("password123")
    user = User(username="testuser", email="test@example.com", password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    with client:
        # First get the login page to establish session and get CSRF token
        get_response = client.get(url_for('public.login'))
        assert get_response.status_code == 200
        
        # Extract CSRF token using BeautifulSoup
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        
        # Test with invalid CSRF token
        login_response = client.post(url_for('public.login'), data={
            'username': 'testuser',
            'password': 'password123',
            'csrf_token': 'invalid_token'
        })
        
        assert login_response.status_code == 400
        assert b"CSRF token is invalid" in login_response.data
        
        # Test with missing CSRF token
        login_response = client.post(url_for('public.login'), data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        assert login_response.status_code == 400
        # Handle both possible error messages from different Flask-WTF versions
        assert (b"CSRF session token is missing" in login_response.data or 
               b"CSRF token is missing" in login_response.data)

def test_audit_log_table_exists(client):
    """Test that audit_log table exists"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from app.extensions import db
        from sqlalchemy import inspect
        
        # Create inspector
        inspector = inspect(db.engine)
        
        # Get table names
        tables = inspector.get_table_names()
        logger.info(f"Found tables: {tables}")
        
        # Verify audit_log exists
        assert 'audit_log' in tables, "audit_log table does not exist"
        
    except Exception as e:
        logger.error(f"Error checking audit_log table: {str(e)}")
        raise

def test_profile_form_rate_limiting(client, setup_database):
    """Test profile form submissions with rate limiting disabled"""
    # Create test user
    password_hash = generate_password_hash("password123")
    user = User(username="testuser", email="test@example.com", password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    with client:
        # Ensure rate limiting is disabled at both config and limiter levels
        current_app.config['RATELIMIT_ENABLED'] = False
        if 'limiter' in current_app.extensions:
            current_app.extensions['limiter'].enabled = False

        # First make a GET request to establish session and get CSRF token
        get_response = client.get(url_for('public.login'))
        assert get_response.status_code == 200

        # Extract CSRF token using BeautifulSoup
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        assert csrf_token, "CSRF token not found in form"

        # Login user
        login_response = client.post(url_for('public.login'), data={
            'username': 'testuser',
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert login_response.status_code == 200, "Login failed"

        # Get initial CSRF token from the profile edit page
        get_response = client.get(url_for('user.edit_profile'))
        assert get_response.status_code == 200, "Failed to access profile edit page"
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        assert csrf_token, "CSRF token not found in profile form"

        # Submit profile form multiple times to verify rate limiting is disabled
        responses = []
        for i in range(20):  # Test up to the limit
            response = client.post(url_for('user.edit_profile'), data={
                'username': 'testuser',
                'email': 'test@example.com',
                'csrf_token': csrf_token
            }, follow_redirects=True)
            responses.append(response.status_code)
            
            # Refresh CSRF token every 5 requests with debug logging
            if i > 0 and i % 5 == 0:
                get_response = client.get(url_for('user.edit_profile'))
                print(f"CSRF refresh response status: {get_response.status_code}")  # Debug logging
                assert get_response.status_code == 200, f"Failed to refresh CSRF token after {i} requests"
                soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
            
            # Add small delay between requests
            time.sleep(0.1)
    
        # Verify all requests were successful
        assert all(r == 200 for r in responses), "Some requests failed unexpectedly"
        
        # Additional verification that rate limiting was truly disabled
        if 'limiter' in current_app.extensions:
            assert not current_app.extensions['limiter'].enabled, "Rate limiter is still enabled"
        assert not current_app.config['RATELIMIT_ENABLED'], "Rate limiting is still enabled in config"

def test_profile_update_creates_audit_log(client, setup_database):
    """Test that profile updates create audit logs"""
    # Log out any existing session
    client.get(url_for('public.logout'))
    
    # Create test user
    password_hash = generate_password_hash("password123")
    user = User(username="testuser", email="test@example.com", password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    with client:
        # First make a GET request to establish session and get CSRF token
        get_response = client.get(url_for('public.login'))
        
        # Handle redirects by following them
        if get_response.status_code == 302:
            get_response = client.get(get_response.location)
        
        assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}"

        # Extract CSRF token using BeautifulSoup
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        assert csrf_token, "CSRF token not found in form"

        # Login user
        login_response = client.post(url_for('public.login'), data={
            'username': 'testuser',
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert login_response.status_code == 200, "Login failed"

        # Clear any existing audit logs from login
        AuditLog.query.delete()
        db.session.commit()

        # Get CSRF token from the profile edit page
        get_response = client.get(url_for('user.edit_profile'))
        assert get_response.status_code == 200, "Failed to access profile edit page"
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        assert csrf_token, "CSRF token not found in profile form"

        # Submit profile update and follow redirect
        response = client.post(url_for('user.edit_profile'), data={
            'username': 'newusername',
            'email': 'newemail@example.com',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        # Verify successful update
        assert response.status_code == 200, "Profile update failed"
        assert b"Profile updated successfully" in response.data

        # Verify audit log was created
        audit_log = AuditLog.query.filter_by(user_id=user.id).first()
        assert audit_log is not None, "Audit log not created"
        assert audit_log.action == "profile_update", "Incorrect audit log action"
        assert "newusername" in audit_log.details, "Username not in audit log details"
        assert "newemail@example.com" in audit_log.details, "Email not in audit log details"

def test_profile_form_validation_errors(client, setup_database):
    """Test various validation errors in profile form"""
    # Create test user
    password_hash = generate_password_hash("password123")
    user = User(username="testuser", email="test@example.com", password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    with client:
        # First make a GET request to establish session and get CSRF token
        get_response = client.get(url_for('public.login'))
        assert get_response.status_code == 200
        
        # Extract CSRF token using BeautifulSoup
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        assert csrf_token, "CSRF token not found in form"

        # Login user
        login_response = client.post(url_for('public.login'), data={
            'username': 'testuser',
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert login_response.status_code == 200, "Login failed"

        # Get CSRF token from the profile edit page
        get_response = client.get(url_for('user.edit_profile'))
        assert get_response.status_code == 200, "Failed to access profile edit page"
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        assert csrf_token, "CSRF token not found in profile form"

        # Test invalid email format
        response = client.post(url_for('user.edit_profile'), data={
            'username': 'testuser',
            'email': 'invalid-email',
            'csrf_token': csrf_token
        })
        assert response.status_code == 400
        assert b"Invalid email address" in response.data
        
        # Test username too short
        response = client.post(url_for('user.edit_profile'), data={
            'username': 'ab',
            'email': 'test@example.com',
            'csrf_token': csrf_token
        })
        assert response.status_code == 400
        assert b"Field must be between 3 and 50 characters long" in response.data
