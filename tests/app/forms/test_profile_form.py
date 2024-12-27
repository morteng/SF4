from unittest.mock import patch
from flask import url_for
from app.forms.user_forms import ProfileForm
import logging

def test_profile_form_valid(logged_in_client, db_session):
    """Test valid profile form submission with CSRF protection"""
    with logged_in_client.application.test_request_context():
        with patch('app.forms.user_forms.User.query.filter_by') as mock_filter_by:
            # Mock the database queries to return None (no existing user)
            mock_filter_by.return_value.first.return_value = None

            # Use a session transaction to maintain the session
            with logged_in_client.session_transaction() as sess:
                # Create the form and get its CSRF token
                form = ProfileForm(
                    original_username="testuser",
                    original_email="test@example.com"
                )
                csrf_token = form.csrf_token._value()

                # Test the form with valid CSRF token
                form.username.data = "newusername"
                form.email.data = "newemail@example.com"

                # Add comprehensive validation testing
                if not form.validate():
                    logging.error("Form validation errors: %s", form.errors)
                    assert False, f"Form validation failed: {form.errors}"

                assert form.validate() == True
                assert form.csrf_token.validate(form) == True

                # Store the CSRF token in the session
                sess['csrf_token'] = csrf_token

            # Test form submission via POST
            response = logged_in_client.post(url_for('user.edit_profile'), data={
                'username': 'newusername',
                'email': 'newemail@example.com',
                'csrf_token': csrf_token
            }, follow_redirects=True)

            # Add detailed error handling and debugging
            if response.status_code != 200:
                logging.error("Response status: %s", response.status_code)
                logging.error("Response data: %s", response.data)
                assert False, f"Unexpected response status: {response.status_code}"

            assert response.status_code == 200
            assert b"Profile updated successfully" in response.data

def test_profile_form_invalid_csrf(client):
    """Test profile form submission with invalid CSRF token"""
    with client.application.test_request_context():
        with patch('app.forms.user_forms.User.query.filter_by') as mock_filter_by:
            mock_filter_by.return_value.first.return_value = None

            with client.session_transaction() as sess:
                form = ProfileForm(
                    original_username="testuser",
                    original_email="test@example.com"
                )
                csrf_token = form.csrf_token._value()
                sess['csrf_token'] = csrf_token

            # Submit with invalid CSRF token
            response = client.post(url_for('user.edit_profile'), data={
                'username': 'newusername',
                'email': 'newemail@example.com',
                'csrf_token': 'invalid_token'
            }, follow_redirects=True)

            assert response.status_code == 400
            assert b"CSRF token is invalid" in response.data
