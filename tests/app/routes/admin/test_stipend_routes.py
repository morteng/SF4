import pytest
from flask import url_for
from app.models.stipend import Stipend
from app.forms.admin_forms import StipendForm  # Import the StipendForm class
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
def test_stipend(db_session, admin_user):
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
    db_session.add(stipend)
    db_session.flush()
    yield stipend
    db_session.rollback()

def test_create_stipend(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        # Simulate form submission with valid application_deadline and open_for_applications checked
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        if not response.data:
            print("Response is empty")
        else:
            print(response.data.decode())
        
        # Print form validation errors
        form = StipendForm(data=stipend_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
        
        assert response.status_code in (200, 302)
        
        # Check if the stipend was created in the database
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.summary == 'This is a test stipend.'
        assert stipend.description == 'Detailed description of the test stipend.'
        assert stipend.homepage_url == 'http://example.com/stipend'
        assert stipend.application_procedure == 'Apply online at example.com'
        assert stipend.eligibility_criteria == 'Open to all students'
        assert stipend.open_for_applications is True
        assert stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2023-12-31 23:59:59'

def test_create_stipend_with_unchecked_open_for_applications(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        # Simulate form submission with open_for_applications unchecked
        stipend_data_no_open_for_apps = {
            key: value for key, value in stipend_data.items() if key != 'open_for_applications'
        }
        
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data_no_open_for_apps)
        
        if not response.data:
            print("Response is empty")
        else:
            print(response.data.decode())
        
        # Print form validation errors
        form = StipendForm(data=stipend_data_no_open_for_apps)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
        
        assert response.status_code in (200, 302)
        
        # Check if the stipend was created in the database with open_for_applications as False
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.open_for_applications is False

def test_create_stipend_with_blank_application_deadline(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        # Simulate form submission with blank application_deadline
        stipend_data['application_deadline'] = ''
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        if not response.data:
            print("Response is empty")
        else:
            print(response.data.decode())
        
        # Print form validation errors
        form = StipendForm(data=stipend_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
        
        assert response.status_code in (200, 302)
        
        # Check if the stipend was created in the database with application_deadline as None
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.application_deadline is None

def test_create_stipend_with_invalid_application_deadline(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        # Simulate form submission with invalid application_deadline
        stipend_data['application_deadline'] = 'invalid-date'
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        if not response.data:
            print("Response is empty")
        else:
            print(response.data.decode())
        
        # Print form validation errors
        form = StipendForm(data=stipend_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
        
        assert response.status_code in (200, 302)
        
        # Check if the stipend was created in the database with application_deadline as None
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.application_deadline is None

def test_create_stipend_with_htmx(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        # Simulate form submission with valid application_deadline using HTMX headers
        response = logged_in_admin.post(
            url_for('admin.stipend.create'),
            data=stipend_data,
            headers={
                'HX-Request': 'true',
                'HX-Target': '#stipend-form-container'
            }
        )
        
        if not response.data:
            print("Response is empty")
        else:
            print(response.data.decode())
        
        # Print form validation errors
        form = StipendForm(data=stipend_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
        
        assert response.status_code == 200

        # Check if the stipend was created in the database
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.summary == 'This is a test stipend.'
        assert stipend.description == 'Detailed description of the test stipend.'
        assert stipend.homepage_url == 'http://example.com/stipend'
        assert stipend.application_procedure == 'Apply online at example.com'
        assert stipend.eligibility_criteria == 'Open to all students'
        assert stipend.open_for_applications is True
        assert stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2023-12-31 23:59:59'

        assert b'id="stipend-form-container"' in response.data  # Validate target container exists

def test_create_stipend_with_blank_application_deadline_htmx(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        # Simulate form submission with blank application_deadline using HTMX headers
        stipend_data['application_deadline'] = ''
        response = logged_in_admin.post(
            url_for('admin.stipend.create'),
            data=stipend_data,
            headers={
                'HX-Request': 'true',
                'HX-Target': '#stipend-form-container'
            }
        )

        if not response.data:
            print("Response is empty")
        else:
            print(response.data.decode())
        
        # Print form validation errors
        form = StipendForm(data=stipend_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
        
        assert response.status_code == 200

        # Check if the stipend was created in the database with application_deadline as None
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.application_deadline is None

        assert b'id="stipend-form-container"' in response.data  # Validate target container exists

def test_create_stipend_with_invalid_application_deadline_htmx(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        # Simulate form submission with invalid application_deadline using HTMX headers
        stipend_data['application_deadline'] = 'invalid-date'
        response = logged_in_admin.post(
            url_for('admin.stipend.create'),
            data=stipend_data,
            headers={
                'HX-Request': 'true',
                'HX-Target': '#stipend-form-container'
            }
        )

        if not response.data:
            print("Response is empty")
        else:
            print(response.data.decode())
        
        # Print form validation errors
        form = StipendForm(data=stipend_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
        
        assert response.status_code == 200

        # Check if the stipend was created in the database with application_deadline as None
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is not None
        assert stipend.application_deadline is None

        assert b'id="stipend-form-container"' in response.data  # Validate target container exists

def test_update_stipend(logged_in_admin, test_stipend, db_session):
    with logged_in_admin.application.app_context():
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

        assert updated_data['application_deadline'] == '2024-12-31 23:59:59'  # Sanity check

        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)

        if not response.data:
            print("Response is empty")
        else:
            print(response.data.decode())
        
        # Print form validation errors
        form = StipendForm(data=updated_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
        
        assert response.status_code in (200, 302)

        # Check if the stipend was updated in the database
        stipend = db_session.get(Stipend, test_stipend.id)
        assert stipend.name == updated_data['name']
        assert stipend.summary == "Updated summary."
        assert stipend.description == "Updated description."
        assert stipend.homepage_url == "http://example.com/updated-stipend"
        assert stipend.application_procedure == "Apply online at example.com/updated"
        assert stipend.eligibility_criteria == "Open to all updated students"
        assert stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2024-12-31 23:59:59'

def test_update_stipend_with_unchecked_open_for_applications(logged_in_admin, test_stipend, db_session):
    with logged_in_admin.application.app_context():
        updated_data_no_open_for_apps = {
            'name': test_stipend.name,  # Retain the original name
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2024-12-31 23:59:59',
        }

        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data_no_open_for_apps)

        if not response.data:
            print("Response is empty")
        else:
            print(response.data.decode())
        
        # Print form validation errors
        form = StipendForm(data=updated_data_no_open_for_apps)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
        
        assert response.status_code in (200, 302)

        # Check if the stipend was updated in the database with open_for_applications as False
        stipend = db_session.get(Stipend, test_stipend.id)
        assert stipend.open_for_applications is False

def test_update_stipend_with_blank_application_deadline(logged_in_admin, test_stipend, db_session):
    with logged_in_admin.application.app_context():
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

        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)
        
        if not response.data:
            print("Response is empty")
        else:
            print(response.data.decode())
        
        # Print form validation errors
        form = StipendForm(data=updated_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
        
        assert response.status_code in (200, 302)

        # Check if the stipend was updated in the database with application_deadline as None
        stipend = db_session.get(Stipend, test_stipend.id)
        assert stipend.application_deadline is None

def test_update_stipend_with_invalid_application_deadline(logged_in_admin, test_stipend, db_session):
    with logged_in_admin.application.app_context():
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

        response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data)
        
        if not response.data:
            print("Response is empty")
        else:
            print(response.data.decode())
        
        # Print form validation errors
        form = StipendForm(data=updated_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
        
        assert response.status_code in (200, 302)

        # Check if the stipend was updated in the database with application_deadline as None
        stipend = db_session.get(Stipend, test_stipend.id)
        assert stipend.application_deadline is None

def test_delete_stipend(logged_in_admin, test_stipend, db_session):
    with logged_in_admin.application.app_context():
        print(f"Type of test_stipend: {type(test_stipend)}")
        print(f"ID of test_stipend: {test_stipend.id}")
        
        # Log the type and value of the ID being passed to the delete endpoint
        logging.info(f"Deleting stipend with ID: {test_stipend.id}")
        response = logged_in_admin.post(url_for('admin.stipend.delete', id=test_stipend.id))
        
        if not response.data:
            print("Response is empty")
        else:
            print(response.data.decode())
        
        assert response.status_code in (200, 302)

        # Check if the stipend was deleted from the database
        stipend = db_session.get(Stipend, test_stipend.id)
        assert stipend is None

def test_delete_non_existent_stipend(logged_in_admin):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.stipend.delete', id=999))
        
        if not response.data:
            print("Response is empty")
        else:
            print(response.data.decode())
        
        assert response.status_code == 302
        assert response.location.endswith('/admin/stipends/')
