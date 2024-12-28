from unittest.mock import patch
from app.utils import db_session_scope
from flask import url_for
from flask_wtf.csrf import generate_csrf
from app.forms.user_forms import ProfileForm
from app.constants import FlashMessages
from app.models.user import User
from tests.conftest import extract_csrf_token
import logging

def test_profile_form_valid(logged_in_client, db_session, test_user):
    """Test valid profile form submission with CSRF protection"""
    with logged_in_client.application.app_context():
        # Get CSRF token from edit profile page
        edit_profile_response = logged_in_client.get(url_for('user.edit_profile'))
        csrf_token = extract_csrf_token(edit_profile_response.data)
        assert csrf_token is not None, "CSRF token not found in response."

        # Test form submission
        with logged_in_client.session_transaction() as session:
            session['_csrf_token'] = csrf_token

        response = logged_in_client.post(url_for('user.edit_profile'), data={
            'username': 'newusername',
            'email': 'newemail@example.com',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.data.decode('utf-8')}"
        assert FlashMessages.PROFILE_UPDATE_SUCCESS.value.encode() in response.data
        
        # Verify the user was actually updated in the database
        updated_user = db_session.query(User).filter_by(id=test_user.id).first()
        assert updated_user is not None, "User not found in database"
        assert updated_user.username == 'newusername'
        assert updated_user.email == 'newemail@example.com'

def test_profile_form_invalid_email(logged_in_client, db_session, test_user):
    """Test profile form with invalid email format"""
    with logged_in_client.application.app_context():
        # Get CSRF token
        edit_response = logged_in_client.get(url_for('user.edit_profile'))
        csrf_token = extract_csrf_token(edit_response.data)
        
        # Submit invalid email
        response = logged_in_client.post(url_for('user.edit_profile'), data={
            'username': 'validusername',
            'email': 'invalid-email',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        assert response.status_code == 400
        assert b"Invalid email address" in response.data

def test_profile_form_duplicate_username(logged_in_client, db_session, test_user):
    """Test profile form with duplicate username"""
    with logged_in_client.application.app_context():
        # Create another user
        other_user = User(username='existinguser', email='other@example.com')
        db_session.add(other_user)
        db_session.commit()
        
        # Get CSRF token
        edit_response = logged_in_client.get(url_for('user.edit_profile'))
        csrf_token = extract_csrf_token(edit_response.data)
        
        # Submit duplicate username
        response = logged_in_client.post(url_for('user.edit_profile'), data={
            'username': 'existinguser',
            'email': 'unique@example.com',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        assert response.status_code == 400
        assert b"Username already exists" in response.data

def test_profile_form_invalid_csrf(logged_in_client):
    """Test form submission with invalid CSRF token"""
    response = logged_in_client.post(url_for('user.edit_profile'), data={
        'username': 'newusername',
        'email': 'newemail@example.com',
        'csrf_token': 'invalid_token'
    }, follow_redirects=True)
    
    assert response.status_code == 400
    assert b"CSRF token is invalid" in response.data

def test_profile_form_missing_fields(logged_in_client):
    """Test form submission with missing required fields"""
    # Get CSRF token first
    edit_profile_response = logged_in_client.get(url_for('user.edit_profile'))
    csrf_token = extract_csrf_token(edit_profile_response.data)
    
    response = logged_in_client.post(url_for('user.edit_profile'), data={
        'username': '',
        'email': '',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 400
    
    # Check for validation error messages in the response
    assert b"Username is required" in response.data
    assert b"Email is required" in response.data
    
    # Check for error message in the response HTML
    assert b"Please correct the errors below" in response.data

def test_profile_form_invalid_csrf(logged_in_client):
    """Test profile form submission with invalid CSRF token"""
    with logged_in_client.application.test_request_context():
        with patch('app.forms.user_forms.User.query.filter_by') as mock_filter_by:
            mock_filter_by.return_value.first.return_value = None

            # Log out first to ensure the login page is accessible
            logged_in_client.get(url_for('public.logout'))

            # Get valid CSRF token from login page
            login_response = logged_in_client.get(url_for('public.login'))
            valid_csrf = extract_csrf_token(login_response.data)

            # Submit with invalid CSRF token
            response = logged_in_client.post(url_for('user.edit_profile'), data={
                'username': 'newusername',
                'email': 'newemail@example.com',
                'csrf_token': 'invalid_token'
            }, follow_redirects=True)

            assert response.status_code == 400
            assert FlashMessages.CSRF_INVALID.value.encode() in response.data
            # Verify that the user's profile was not updated
            mock_filter_by.assert_not_called()
