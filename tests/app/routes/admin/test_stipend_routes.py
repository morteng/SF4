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
        'application_deadline': '2023-12-31 23:59:59',  # Valid datetime format
        'open_for_applications': True
    }

def test_create_stipend(client, app, stipend_data, admin_user):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('admin.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200
        
        # Simulate form submission with valid application_deadline
        response = client.post(url_for('admin.admin_stipend.create'), data=stipend_data, follow_redirects=True)
        
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
        assert stipend.application_deadline is not None

def test_create_stipend_with_blank_application_deadline(client, app, stipend_data, admin_user):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('admin.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200
        
        # Simulate form submission with blank application_deadline
        stipend_data['application_deadline'] = ''
        response = client.post(url_for('admin.admin_stipend.create'), data=stipend_data, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check if the stipend was created in the database with application_deadline as None
        stipend = Stipend.query.filter_by(name='Test Stipend').first()
        assert stipend is not None
        assert stipend.application_deadline is None

def test_create_stipend_with_invalid_application_deadline(client, app, stipend_data, admin_user):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('admin.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200
        
        # Simulate form submission with invalid application_deadline
        stipend_data['application_deadline'] = 'invalid-date'
        response = client.post(url_for('admin.admin_stipend.create'), data=stipend_data, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check if the stipend was created in the database with application_deadline as None
        stipend = Stipend.query.filter_by(name='Test Stipend').first()
        assert stipend is not None
        assert stipend.application_deadline is None
