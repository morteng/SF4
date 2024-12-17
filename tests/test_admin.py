import pytest
from flask import url_for

def extract_csrf_token(response_data):
    import re
    csrf_regex = r'<input[^>]+name="csrf_token"[^>]+value="([^"]+)"'
    match = re.search(csrf_regex, response_data.decode('utf-8'))
    if match:
        return match.group(1)
    return None

def test_create_organization_with_special_characters(logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        data = {
            'name': '<script>alert("XSS")</script>',  # Special characters
            'description': 'Test Description',
            'homepage_url': 'http://example.com',
            'csrf_token': csrf_token
        }

        response = logged_in_admin.post(url_for('admin.organization.create'), data=data)

        if response.status_code != 200:
            print(f"Response status code: {response.status_code}")
            form_errors = response.get_data(as_text=True)
            print(f"Form errors: {form_errors}")

        assert response.status_code == 200
