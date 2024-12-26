from flask import url_for, render_template_string, get_flashed_messages
import logging  # Import the logging module
from app.models.stipend import Stipend
from tests.conftest import logged_in_admin, db_session, stipend_data
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_ERROR, FLASH_CATEGORY_SUCCESS  # Import the constants

def test_create_stipend_with_invalid_form_data_htmx(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['name'] = ''  # Intentionally invalid
        response = logged_in_admin.post(
            url_for('admin.stipend.create'),
            data=stipend_data,
            headers={
                'HX-Request': 'true',
                'HX-Target': '#stipend-form-container'
            }
        )

        assert response.status_code == 400  # Ensure status code is 400 for invalid data
        assert b'Name is required.' in response.data  # Updated to match the actual error message

def test_create_stipend_with_invalid_application_deadline(stipend_data, logged_in_admin, db_session):
    test_cases = [
        ('2023-13-32 99:99:99', 'Invalid date values (e.g., Feb 30)'),
        ('2023-02-30 12:00:00', 'Invalid date values (e.g., Feb 30)'),
        ('2023-01-01 25:61:61', 'Invalid time values (e.g., 25:61:61)'),
        ('2023-01-01', 'Time is required. Please use YYYY-MM-DD HH:MM:SS'),
        ('', 'Date is required'),
        ('2020-01-01 00:00:00', 'Application deadline must be a future date'),
        ('2030-01-01 00:00:00', 'Application deadline cannot be more than 5 years in the future'),
        ('2023-02-29 12:00:00', 'Invalid date values (e.g., Feb 30)'),  # Test leap year
        ('2023-04-31 12:00:00', 'Invalid date values (e.g., Feb 30)'),  # Test invalid month day
        ('2023-01-01 24:00:00', 'Invalid time values (e.g., 25:61:61)'),  # Test invalid hour
        ('invalid-date', 'Invalid date format. Please use YYYY-MM-DD HH:MM:SS'),  # Test invalid format
        ('2023-01-01 12:00', 'Time is required. Please use YYYY-MM-DD HH:MM:SS')  # Test missing seconds
    ]

    with logged_in_admin.application.app_context():
        for date_str, expected_error in test_cases:
            stipend_data['application_deadline'] = date_str
            response = logged_in_admin.post(
                url_for('admin.stipend.create'),
                data=stipend_data,
                headers={
                    'HX-Request': 'true',
                    'HX-Target': '#stipend-form-container'
                }
            )

            assert response.status_code == 400
            assert expected_error.encode() in response.data
            assert b'application_deadline' in response.data
            assert b'is-invalid' in response.data
            # Verify error message appears in the form
            assert b'id="application_deadline-error"' in response.data

def test_create_stipend_with_past_date(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['application_deadline'] = '2020-01-01 00:00:00'  # Past date
        response = logged_in_admin.post(
            url_for('admin.stipend.create'),
            data=stipend_data,
            headers={
                'HX-Request': 'true',
                'HX-Target': '#stipend-form-container'
            }
        )
        assert response.status_code == 400
        assert b'Application deadline cannot be in the past' in response.data

def test_create_stipend_with_far_future_date(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['application_deadline'] = '2030-01-01 00:00:00'  # More than 5 years
        response = logged_in_admin.post(
            url_for('admin.stipend.create'),
            data=stipend_data,
            headers={
                'HX-Request': 'true',
                'HX-Target': '#stipend-form-container'
            }
        )
        assert response.status_code == 400
        assert b'Application deadline cannot be more than 5 years in the future' in response.data

