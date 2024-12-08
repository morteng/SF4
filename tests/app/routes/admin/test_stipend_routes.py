# tests/app/routes/admin/test_stipend_routes.py
import pytest
from flask import url_for
from app.models.stipend import Stipend
from app.extensions import db
from datetime import datetime

@pytest.fixture
def stipend_data(request):
    return {
        'name': f"Test Stipend {request.node.name}",
        'summary': 'This is a test stipend.',
        'description': 'Detailed description of the test stipend.',
        'homepage_url': 'http://example.com/stipend',
        'application_procedure': 'Apply online at example.com',
        'eligibility_criteria': 'Open to all students',
        'application_deadline': '2023-12-31 23:59:59',  # Valid datetime format
        'open_for_applications': True
    }

@pytest.fixture
def test_stipend(db, admin_user):
    with db.begin():
        stipend = Stipend(
            name="Test Stipend",
            summary="This is a test stipend.",
            description="Detailed description of the test stipend.",
            homepage_url="http://example.com/stipend",
            application_procedure="Apply online at example.com",
            eligibility_criteria="Open to all students",
            application_deadline=datetime.strptime('2023-12-31 23:59:59', '%Y-%m-%d %H:%M:%S'),
            open_for_applications=True
        )
        db.add(stipend)
    return stipend

def test_create_stipend(client, app, stipend_data, admin_user):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('public.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200
        
        # Ensure application_deadline is a string
        stipend_data['application_deadline'] = '2023-12-31 23:59:59'
        
        # Simulate form submission with valid application_deadline and open_for_applications checked
        response = client.post(url_for('admin.admin_stipend.create'), data=stipend_data, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check if the stipend was created in the database
        stipend = Stipend.query.filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.summary == 'This is a test stipend.'
        assert stipend.description == 'Detailed description of the test stipend.'
        assert stipend.homepage_url == 'http://example.com/stipend'
        assert stipend.application_procedure == 'Apply online at example.com'
        assert stipend.eligibility_criteria == 'Open to all students'
        assert stipend.open_for_applications is True
        assert stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2023-12-31 23:59:59'

def test_create_stipend_with_unchecked_open_for_applications(client, app, stipend_data, admin_user):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('public.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200
        
        # Simulate form submission with open_for_applications unchecked
        stipend_data_no_open_for_apps = {
            key: value for key, value in stipend_data.items() if key != 'open_for_applications'
        }
        
        response = client.post(url_for('admin.admin_stipend.create'), data=stipend_data_no_open_for_apps, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check if the stipend was created in the database with open_for_applications as False
        stipend = Stipend.query.filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.open_for_applications is False

def test_create_stipend_with_blank_application_deadline(client, app, stipend_data, admin_user):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('public.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200
        
        # Simulate form submission with blank application_deadline
        stipend_data['application_deadline'] = ''
        response = client.post(url_for('admin.admin_stipend.create'), data=stipend_data, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check if the stipend was created in the database with application_deadline as None
        stipend = Stipend.query.filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.application_deadline is None

def test_create_stipend_with_invalid_application_deadline(client, app, stipend_data, admin_user):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('public.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200
        
        # Simulate form submission with invalid application_deadline
        stipend_data['application_deadline'] = 'invalid-date'
        response = client.post(url_for('admin.admin_stipend.create'), data=stipend_data, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check if the stipend was created in the database with application_deadline as None
        stipend = Stipend.query.filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.application_deadline is None

def test_create_stipend_with_htmx(client, app, stipend_data, admin_user):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('public.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200

        # Ensure application_deadline is a string
        stipend_data['application_deadline'] = '2023-12-31 23:59:59'

        # Simulate form submission with valid application_deadline using HTMX headers
        response = client.post(
            url_for('admin.admin_stipend.create'),
            data=stipend_data,
            follow_redirects=True,
            headers={
                'HX-Request': 'true',
                'HX-Target': '#stipend-form-container'
            }
        )

        assert response.status_code == 200

        # Check if the stipend was created in the database
        stipend = Stipend.query.filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.summary == 'This is a test stipend.'
        assert stipend.description == 'Detailed description of the test stipend.'
        assert stipend.homepage_url == 'http://example.com/stipend'
        assert stipend.application_procedure == 'Apply online at example.com'
        assert stipend.eligibility_criteria == 'Open to all students'
        assert stipend.open_for_applications is True
        assert stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2023-12-31 23:59:59'

def test_create_stipend_with_blank_application_deadline_htmx(client, app, stipend_data, admin_user):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('public.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200

        # Simulate form submission with blank application_deadline using HTMX headers
        stipend_data['application_deadline'] = ''
        response = client.post(
            url_for('admin.admin_stipend.create'),
            data=stipend_data,
            follow_redirects=True,
            headers={
                'HX-Request': 'true',
                'HX-Target': '#stipend-form-container'
            }
        )

        assert response.status_code == 200

        # Check if the stipend was created in the database with application_deadline as None
        stipend = Stipend.query.filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.application_deadline is None

def test_create_stipend_with_invalid_application_deadline_htmx(client, app, stipend_data, admin_user):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('public.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200

        # Simulate form submission with invalid application_deadline using HTMX headers
        stipend_data['application_deadline'] = 'invalid-date'
        response = client.post(
            url_for('admin.admin_stipend.create'),
            data=stipend_data,
            follow_redirects=True,
            headers={
                'HX-Request': 'true',
                'HX-Target': '#stipend-form-container'
            }
        )

        assert response.status_code == 200

        # Check if the stipend was created in the database with application_deadline as None
        stipend = Stipend.query.filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.application_deadline is None

def test_update_stipend(client, app, admin_user, test_stipend):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('public.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200

        updated_data = {
            'name': test_stipend.name,  # Retain the original name
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2024-12-31 23:59:59',
            'open_for_applications': True
        }

        response = client.post(url_for('admin.admin_stipend.update', id=test_stipend.id), data=updated_data, follow_redirects=True)
        
        assert response.status_code == 200

        # Check if the stipend was updated in the database
        stipend = Stipend.query.get(test_stipend.id)
        assert stipend.name == test_stipend.name
        assert stipend.summary == "Updated summary."
        assert stipend.description == "Updated description."
        assert stipend.homepage_url == "http://example.com/updated-stipend"
        assert stipend.application_procedure == "Apply online at example.com/updated"
        assert stipend.eligibility_criteria == "Open to all updated students"
        assert stipend.open_for_applications is True
        assert stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2024-12-31 23:59:59'

def test_update_stipend_with_unchecked_open_for_applications(client, app, admin_user, test_stipend):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('public.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200

        updated_data_no_open_for_apps = {
            'name': test_stipend.name,  # Retain the original name
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2024-12-31 23:59:59',
        }

        response = client.post(url_for('admin.admin_stipend.update', id=test_stipend.id), data=updated_data_no_open_for_apps, follow_redirects=True)

        assert response.status_code == 200

        # Check if the stipend was updated in the database with open_for_applications as False
        stipend = Stipend.query.get(test_stipend.id)
        assert stipend.open_for_applications is False

def test_update_stipend_with_blank_application_deadline(client, app, admin_user, test_stipend):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('public.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200

        updated_data = {
            'name': test_stipend.name,  # Retain the original name
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '',
            'open_for_applications': False
        }

        response = client.post(url_for('admin.admin_stipend.update', id=test_stipend.id), data=updated_data, follow_redirects=True)
        
        assert response.status_code == 200

        # Check if the stipend was updated in the database with application_deadline as None
        stipend = Stipend.query.get(test_stipend.id)
        assert stipend.application_deadline is None

def test_update_stipend_with_invalid_application_deadline(client, app, admin_user, test_stipend):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('public.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200

        updated_data = {
            'name': test_stipend.name,  # Retain the original name
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': 'invalid-date',
            'open_for_applications': False
        }

        response = client.post(url_for('admin.admin_stipend.update', id=test_stipend.id), data=updated_data, follow_redirects=True)
        
        assert response.status_code == 200

        # Check if the stipend was updated in the database with application_deadline as None
        stipend = Stipend.query.get(test_stipend.id)
        assert stipend.application_deadline is None

def test_delete_stipend(client, app, admin_user, test_stipend):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('public.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200

        response = client.post(url_for('admin.admin_stipend.delete', id=test_stipend.id), follow_redirects=True)
        
        assert response.status_code == 200

        # Check if the stipend was deleted from the database
        stipend = Stipend.query.get(test_stipend.id)
        assert stipend is None

def test_delete_non_existent_stipend(client, app, admin_user):
    with app.app_context():
        # Log in the admin user
        login_response = client.post(url_for('public.login'), data={'username': admin_user.username, 'password': 'password123'}, follow_redirects=True)
        assert login_response.status_code == 200

        response = client.post(url_for('admin.admin_stipend.delete', id=999), follow_redirects=True)
        
        assert response.status_code == 200
