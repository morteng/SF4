from flask import url_for
from app.models.stipend import Stipend
from tests.conftest import logged_in_admin, stipend_data, db_session
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR
from app.forms.admin_forms import StipendForm  # Added import statement

def test_create_stipend_with_blank_application_deadline(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        # Create a test organization first
        from app.models.organization import Organization
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
            'organization_id': test_org.id,  # Use the actual organization ID
            'open_for_applications': True
        }
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=test_data)
        
        assert response.status_code == 302  # Should redirect on success

        stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
        assert stipend is not None
        assert stipend.application_deadline is None  # Verify the deadline is None

def test_create_stipend_with_invalid_application_deadline(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['application_deadline'] = '2023-13-32 99:99:99'
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 200

        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None
        assert FLASH_MESSAGES["INVALID_DATE_FORMAT"].encode() in response.data

def test_update_stipend_with_blank_application_deadline(logged_in_admin, test_stipend, stipend_data, db_session):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': test_stipend.name,
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '',
            'open_for_applications': True
        }

        response = logged_in_admin.post(url_for('admin.stipend.edit', id=test_stipend.id), data=updated_data)
        
        assert response.status_code in (200, 302)

        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.application_deadline is None

def test_update_stipend_with_invalid_application_deadline(logged_in_admin, test_stipend, stipend_data, db_session):
    with logged_in_admin.application.app_context():
        updated_data = {
            'name': test_stipend.name,
            'summary': "Updated summary.",
            'description': "Updated description.",
            'homepage_url': "http://example.com/updated-stipend",
            'application_procedure': "Apply online at example.com/updated",
            'eligibility_criteria': "Open to all updated students",
            'application_deadline': '2023-13-32 99:99:99',
            'open_for_applications': True
        }

        response = logged_in_admin.post(url_for('admin.stipend.edit', id=test_stipend.id), data=updated_data)
        
        assert response.status_code == 200

        db_session.expire_all()
        stipend = db_session.query(Stipend).filter_by(id=test_stipend.id).first()
        assert stipend.application_deadline == test_stipend.application_deadline
        assert FLASH_MESSAGES["INVALID_DATE_FORMAT"].encode() in response.data  # Check for the specific validation error message

def test_create_stipend_with_invalid_form_data(stipend_data, logged_in_admin, db_session):
    with logged_in_admin.application.app_context():
        stipend_data['name'] = ''
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 200

        form = StipendForm(data=stipend_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
            
        stipend = db_session.query(Stipend).filter_by(name=stipend_data['name']).first()
        assert stipend is None
