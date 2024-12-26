from flask import url_for, render_template_string
import logging  # Import the logging module
from app.models.stipend import Stipend
from tests.conftest import logged_in_admin, db_session, stipend_data
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_ERROR, FLASH_CATEGORY_SUCCESS  # Import the constants

def test_create_stipend_with_invalid_form_data_htmx(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['name'] = ''  # Intentionally invalid
        stipend_data.setdefault('summary', 'Test Summary')
        stipend_data.setdefault('description', 'Test Description')
        stipend_data.setdefault('homepage_url', 'http://example.com')
        stipend_data.setdefault('application_procedure', 'Apply online')
        stipend_data.setdefault('eligibility_criteria', 'Open to all')
        stipend_data.setdefault('application_deadline', '2023-12-31 23:59:59')
        stipend_data.setdefault('open_for_applications', True)
        stipend_data.setdefault('submit', 'Create')

        response = logged_in_admin.post(
            url_for('admin.stipend.create'),
            data=stipend_data,
            headers={
                'HX-Request': 'true',
                'HX-Target': '#stipend-form-container'
            }
        )

        assert response.status_code == 200

        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None

        # Check if the flash message is present in the response data
        assert b'This field is required.' in response.data, "Flash message 'This field is required.' not found in response."

def test_create_stipend_with_invalid_application_deadline(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['application_deadline'] = '2023-13-32 99:99:99'
        response = logged_in_admin.post(
            url_for('admin.stipend.create'),
            data=stipend_data,
            headers={
                'HX-Request': 'true',
                'HX-Target': '#stipend-form-container'
            }
        )

        assert response.status_code == 200

        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None
 
        # Check if the flash message is present in the response data
        assert b'Invalid date format.' in response.data, "Flash message 'Invalid date format.' not found in response."
 

