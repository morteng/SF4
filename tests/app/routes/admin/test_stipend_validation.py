from flask import url_for
from app.models.stipend import Stipend
from tests.conftest import logged_in_admin, stipend_data, db_session
from app.constants import FlashMessages, FlashCategory
from app.forms.admin_forms import StipendForm
from app.models.organization import Organization

def test_create_stipend_with_blank_application_deadline(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        # Create a test organization first
        test_org = Organization(name="Test Org", description="Test Org Description")
        db_session.add(test_org)
        db_session.commit()
        
        # Ensure all required fields are present
        test_data = {
            'name': 'Test Stipend',
            'summary': 'Test summary',
            'description': 'Test description',
            'homepage_url': 'http://example.com',
            'application_procedure': 'Test procedure',
            'eligibility_criteria': 'Test criteria',
            'application_deadline': '',
            'organization_id': test_org.id,
            'open_for_applications': True
       }
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=test_data, follow_redirects=True)
        
        assert response.status_code == 200  # Adjust based on view behavior
    
        stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
        assert stipend is not None
        assert stipend.application_deadline is None  # Verify the deadline is None

def test_create_stipend_with_invalid_application_deadline(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['application_deadline'] = '2023-13-32 99:99:99'  # Invalid date
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data, follow_redirects=True)
        
        assert response.status_code == 200  # Adjust based on view behavior
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None
        
        # Check for flash message in response
        assert FlashMessages.INVALID_DATE_FORMAT in response.get_data(as_text=True)

def test_update_stipend_with_blank_application_deadline(logged_in_admin, test_stipend, stipend_data, db_session):
    with logged_in_admin.application.app_context():
        # Ensure the stipend is attached to the current session
        test_stipend = db_session.merge(test_stipend)
        
        updated_data = {
            'name': test_stipend.name,
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '',
            'organization_id': test_stipend.organization.id,
            'open_for_applications': True
        }
 
        response = logged_in_admin.post(url_for('admin.stipend.edit', id=test_stipend.id), data=updated_data, follow_redirects=True)
        
        assert response.status_code == 200  # Adjust based on view behavior

        # Refresh the instance from the database
        db_session.refresh(test_stipend)
        assert test_stipend.application_deadline is None

def test_update_stipend_with_invalid_application_deadline(logged_in_admin, test_stipend, stipend_data, db_session):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': test_stipend.name,
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2023-13-32 99:99:99',  # Invalid date
            'open_for_applications': True
        }
 
        response = logged_in_admin.post(url_for('admin.stipend.edit', id=test_stipend.id), data=updated_data, follow_redirects=True)
        
        assert response.status_code == 200  # Adjust based on view behavior
        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.application_deadline == test_stipend.application_deadline  # Should remain unchanged
        assert FlashMessages.INVALID_DATE_FORMAT in response.get_data(as_text=True)

def test_create_stipend_with_invalid_form_data(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['name'] = ''  # Invalid name
        
        # Ensure 'organization_id' is present
        if 'organization_id' not in stipend_data or not stipend_data['organization_id']:
            # Create a test organization if not present
            test_org = Organization(name="Test Org for Invalid Form", description="Description")
            db_session.add(test_org)
            db_session.commit()
            stipend_data['organization_id'] = test_org.id
        
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data, follow_redirects=True)
        
        # Depending on your view, adjust the expected status code
        assert response.status_code == 200  # Likely re-renders the form with errors
        
        form = StipendForm(data=stipend_data)
        assert not form.validate()
        assert 'This field is required.' in form.name.errors  # Assuming WTForms default message
        
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None
