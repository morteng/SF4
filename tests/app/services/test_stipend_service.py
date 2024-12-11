import pytest
from app.models.stipend import Stipend
from app.services.stipend_service import create_stipend, update_stipend, delete_stipend
from datetime import datetime
from flask_login import login_user
from app.extensions import db  # Ensure consistent session usage
from app.forms.admin_forms import StipendForm

@pytest.fixture
def test_data():
    return {
        'name': "Test Stipend",
        'summary': 'This is a test stipend.',
        'description': 'Detailed description of the test stipend.',
        'homepage_url': 'http://example.com/stipend',
        'application_procedure': 'Apply online at example.com',
        'eligibility_criteria': 'Open to all students',
        'application_deadline': datetime.strptime('2023-12-31 23:59:59', '%Y-%m-%d %H:%M:%S'),
        'open_for_applications': True
    }

def test_create_stipend(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)

    with app.app_context(), app.test_request_context():
        login_user(admin_user)
        create_stipend(stipend, session=db_session)  # Add and commit the stipend

    # Query the stipend from the session to ensure it's bound
    new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()

    # Check if the stipend was created successfully
    assert new_stipend is not None
    assert new_stipend.name == test_data['name']
    assert new_stipend.summary == test_data['summary']
    assert new_stipend.description == test_data['description']
    assert new_stipend.homepage_url == test_data['homepage_url']
    assert new_stipend.application_procedure == test_data['application_procedure']
    assert new_stipend.eligibility_criteria == test_data['eligibility_criteria']
    assert new_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2023-12-31 23:59:59'
    assert new_stipend.open_for_applications is True

def test_create_stipend_with_invalid_application_deadline_format(test_data, db_session, app, admin_user):
    # Modify test data with an invalid application_deadline format
    test_data['application_deadline'] = '2023-13-32 99:99:99'
    
    form = StipendForm(data=test_data)
    
    with app.app_context(), app.test_request_context():
        login_user(admin_user)
        
        # Validate the form
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
            
            # Assert that there are validation errors
            assert 'application_deadline' in form.errors
            
            return
        
        stipend_data = {k: v for k, v in form.data.items() if k != 'submit'}
        stipend = Stipend(**stipend_data)
        new_stipend = create_stipend(stipend, session=db_session)

    # Assert that the stipend was not created due to validation errors
    new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
    assert new_stipend is None
