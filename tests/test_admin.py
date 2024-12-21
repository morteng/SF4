import pytest
from flask import url_for
from app.constants import FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR, FLASH_MESSAGES

def extract_csrf_token(response_data):
    import re
    csrf_regex = r'<input[^>]+name="csrf_token"[^>]+value="([^"]+)"'
    match = re.search(csrf_regex, response_data.decode('utf-8'))
    if match:
        return match.group(1)
    return None

def test_create_stipend_with_valid_data(logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.stipend.create'))
        csrf_token = extract_csrf_token(response.data)

        data = {
            'name': 'Test Stipend',
            'amount': 1000,
            'description': 'Test Description',
            'start_date': '2023-10-01 00:00:00',
            'end_date': '2023-10-31 23:59:59',
            'csrf_token': csrf_token
        }

        response = logged_in_admin.post(url_for('admin.stipend.create'), data=data)

        assert response.status_code == 302  # Redirect to index page on success

        # Check flash messages
        with logged_in_admin.session_transaction() as sess:
            flashes = sess['_flashes']
            assert len(flashes) == 1
            (category, message) = flashes[0]
            assert category == FLASH_CATEGORY_SUCCESS
            assert message == FLASH_MESSAGES["CREATE_STIPEND_SUCCESS"]

def test_create_stipend_with_invalid_form_data(logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.stipend.create'))
        csrf_token = extract_csrf_token(response.data)

        data = {
            'name': '',  # Invalid: name is required
            'amount': 1000,
            'description': 'Test Description',
            'start_date': '2023-10-01 00:00:00',
            'end_date': '2023-10-31 23:59:59',
            'csrf_token': csrf_token
        }

        response = logged_in_admin.post(url_for('admin.stipend.create'), data=data)

        assert response.status_code == 200  # Render form again on error

        # Check flash messages
        with logged_in_admin.session_transaction() as sess:
            flashes = sess['_flashes']
            assert len(flashes) >= 1  # At least one flash message for the invalid field
            (category, message) = flashes[0]
            assert category == FLASH_CATEGORY_ERROR
            assert "name: This field is required." in message  # Specific validation error message

        # Check general form error message
        with logged_in_admin.session_transaction() as sess:
            flashes = sess['_flashes']
            assert any("CREATE_STIPEND_INVALID_FORM" in msg for _, msg in flashes)
