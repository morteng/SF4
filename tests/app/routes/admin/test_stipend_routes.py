import pytest
from flask import url_for
from app.models.stipend import Stipend

@pytest.fixture
def stipend_data():
    return {
        'name': 'Test Stipend',
        'summary': 'This is a test stipend.',
        'description': 'Detailed description of the test stipend.',
        'homepage_url': 'http://example.com/stipend',
        'application_procedure': 'Apply online at example.com',
        'eligibility_criteria': 'Open to all students',
        'application_deadline': '2023-12-31',
        'open_for_applications': True
    }

def test_create_stipend(client, app, stipend_data, admin_user):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('admin.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200
        
        # Simulate form submission
        response = client.post(url_for('admin.stipend.create'), data=stipend_data, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check if the stipend was created in the database
        stipend = Stipend.query.filter_by(name='Test Stipend').first()
        assert stipend is not None
        assert stipend.summary == 'This is a test stipend.'
        assert stipend.description == 'Detailed description of the test stipend.'
        assert stipend.homepage_url == 'http://example.com/stipend'
        assert stipend.application_procedure == 'Apply online at example.com'
        assert stipend.eligibility_criteria == 'Open to all students'
        assert stipend.open_for_applications is True
