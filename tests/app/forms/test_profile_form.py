from unittest.mock import patch
from flask import url_for
from flask_wtf.csrf import generate_csrf
from app.forms.user_forms import ProfileForm
from app.constants import FlashMessages
from tests.conftest import extract_csrf_token
import logging

def test_profile_form_valid(logged_in_client, db_session, test_user):
    """Test valid profile form submission with CSRF protection"""
    with logged_in_client.application.test_request_context('/user/profile/edit'):
        # Test form submission
        response = logged_in_client.post('/user/profile/edit', data={
            'username': 'newusername',
            'email': 'newemail@example.com',
            'csrf_token': generate_csrf()
        })
        assert response.status_code == 302  # Should redirect

        # Use a session transaction to maintain the session
        with logged_in_client.session_transaction() as sess:
            # Create the form with the test user's current credentials
            form = ProfileForm(
                original_username=test_user.username,
                original_email=test_user.email
            )

            # Test the form with valid CSRF token
            form.username.data = "newusername"
            form.email.data = "newemail@example.com"

            # Add comprehensive validation testing
            if not form.validate():
                logging.error("Form validation errors: %s", form.errors)
                assert False, f"Form validation failed: {form.errors}"

            assert form.validate() == True
            assert form.csrf_token.validate(form) == True

            # Store the form data in the session for the POST request
            sess['form_data'] = {
                'username': 'newusername',
                'email': 'newemail@example.com',
                'csrf_token': form.csrf_token.data
            }

        # Test form submission via POST using the same session
        response = logged_in_client.post(url_for('user.edit_profile'), 
            data=sess['form_data'],
            follow_redirects=True)

        # Add detailed error handling and debugging
        if response.status_code != 200:
            logging.error("Response status: %s", response.status_code)
            logging.error("Response data: %s", response.data)
            assert False, f"Unexpected response status: {response.status_code}"

        assert response.status_code == 200
        assert b"Profile updated successfully" in response.data

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
