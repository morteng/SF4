import pytest
from unittest.mock import patch
from flask import session, url_for, current_app
from flask_limiter import Limiter
from bs4 import BeautifulSoup
from werkzeug.security import generate_password_hash
from bs4 import BeautifulSoup

from app.forms.user_forms import ProfileForm, LoginForm
from app import create_app
from app.models.user import User
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
    # Increase rate limit for testing
    current_app.config['RATELIMIT_DEFAULT'] = "10 per minute"
    
    # Create a test user
    password_hash = generate_password_hash("password123")
    user = User(username="testuser", email="test@example.com", password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    
    # Log in the user
    with client:
        # Only reset limiter if rate limiting is enabled
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
    
        # Only reset limiter if rate limiting is enabled
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
            
        # Check for both possible success status codes
        assert login_response.status_code in [200, 302], \
            f"Expected 200 or 302, got {login_response.status_code}"
    
        # Only reset limiter if rate limiting is enabled
        if current_app.config.get('RATELIMIT_ENABLED', True):
            limiter = current_app.extensions.get('limiter')
            if limiter and limiter._storage:  # Check if limiter is properly initialized
                limiter.reset()
        
        # Now access the profile edit page
        get_response = client.get(url_for('user.edit_profile'))
        assert get_response.status_code == 200
        
        # Extract CSRF token using BeautifulSoup
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

        # Only reset limiter if rate limiting is enabled
        if current_app.config.get('RATELIMIT_ENABLED', True):
            limiter = current_app.extensions.get('limiter')
            if limiter and limiter._storage:  # Check if limiter is properly initialized
                limiter.reset()
        
        # Test form submission via POST with valid data
        response = client.post(url_for('user.edit_profile'), data={
            'username': 'newusername',
            'email': 'newemail@example.com',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        # Verify the response
        assert response.status_code == 200
        assert b"Profile updated successfully" in response.data

        # Clean up
        db.session.delete(user)
        db.session.commit()

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
        # Reset rate limiter before first request
        limiter = current_app.extensions.get('limiter')
        limiter.reset()
        
        # First make a GET request to establish session and get CSRF token
        get_response = client.get(url_for('public.login'))
        assert get_response.status_code == 200
            
        # Extract CSRF token using BeautifulSoup
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

        # Reset rate limiter before login attempt
        limiter.reset()
            
        # Now make the login POST request
        login_response = client.post(url_for('public.login'), data={
            'username': 'testuser',
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert login_response.status_code == 200, "Login failed"
        
        # Reset rate limiter before profile edit request
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
