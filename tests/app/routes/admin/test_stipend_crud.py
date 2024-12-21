import pytest
from flask import url_for
from app.constants import FLASH_CATEGORY_SUCCESS, FLASH_MESSAGES

def extract_csrf_token(response_data):
    match = re.search(r'name="csrf_token".*?value="(.+?)"', response_data.decode('utf-8'))
    return match.group(1) if match else "dummy_csrf_token"

def test_update_stipend_with_valid_data(logged_in_admin, test_stipend, stipend_data, db_session):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': 'Updated Stipend',
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2025-12-31 23:59:59',
            'open_for_applications': True
        }
        
        # Extract CSRF token from the form page
        response = logged_in_admin.get(url_for('admin.stipend.edit', id=test_stipend.id))
        csrf_token = extract_csrf_token(response.data)
        updated_data['csrf_token'] = csrf_token

        response = logged_in_admin.post(url_for('admin.stipend.edit', id=test_stipend.id), data=updated_data)

        assert response.status_code == 302  # Redirect to index page on success

        # Check flash messages
        with logged_in_admin.session_transaction() as sess:
            flashes = sess['_flashes']
            assert len(flashes) == 1
            (category, message) = flashes[0]
            assert category == FLASH_CATEGORY_SUCCESS
            assert message == FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"]

        # Verify the stipend was updated in the database
        updated_stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert updated_stipend.name == 'Updated Stipend'
        assert updated_stipend.summary == "Updated summary."
        assert updated_stipend.description == "Updated description."
        assert updated_stipend.homepage_url == "http://example.com/updated-stipend"
        assert updated_stipend.application_procedure == "Apply online at example.com/updated"
        assert updated_stipend.eligibility_criteria == "Open to all updated students"
        assert updated_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2025-12-31 23:59:59'
        assert updated_stipend.open_for_applications is True
