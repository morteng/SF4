import pytest
from app.models.stipend import Stipend
from app.services.stipend_service import create_stipend, update_stipend, delete_stipend, get_stipend_by_id, get_all_stipends
from datetime import datetime
from flask_login import login_user
from app.extensions import db  # Ensure consistent session usage
from app.forms.admin_forms import StipendForm
from app.models.user import User
from app.constants import FLASH_MESSAGES

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

@pytest.fixture
def admin_user(db_session):
    user = User(username='adminuser', email='admin@example.com', password_hash='hashedpassword')
    db_session.add(user)
    db_session.commit()
    return user

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

    # Check if the correct flash message was set
    with app.test_request_context():
        assert len(get_flashed_messages(category_filter=[FLASH_CATEGORY_SUCCESS])) == 1
        assert get_flashed_messages(category_filter=[FLASH_CATEGORY_SUCCESS])[0] == FLASH_MESSAGES["CREATE_STIPEND_SUCCESS"]

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

    # Check if the correct flash message was set
    with app.test_request_context():
        assert len(get_flashed_messages(category_filter=[FLASH_CATEGORY_ERROR])) == 1
        assert get_flashed_messages(category_filter=[FLASH_CATEGORY_ERROR])[0] == FLASH_MESSAGES["INVALID_DATE_FORMAT"]

def test_update_stipend_with_valid_data(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    update_data = {
        'name': "Updated Test Stipend",
        'summary': 'Updated summary',
        'application_deadline': datetime.strptime('2024-12-31 23:59:59', '%Y-%m-%d %H:%M:%S'),
    }

    with app.app_context(), app.test_request_context():
        login_user(admin_user)
        update_stipend(stipend, update_data)

    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
    assert updated_stipend.name == "Updated Test Stipend"
    assert updated_stipend.summary == 'Updated summary'
    assert updated_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2024-12-31 23:59:59'

    # Check if the correct flash message was set
    with app.test_request_context():
        assert len(get_flashed_messages(category_filter=[FLASH_CATEGORY_SUCCESS])) == 1
        assert get_flashed_messages(category_filter=[FLASH_CATEGORY_SUCCESS])[0] == FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"]

def test_update_stipend_with_invalid_application_deadline_format(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    update_data = {
        'application_deadline': '2024-13-32 99:99:99',
    }

    with app.app_context(), app.test_request_context():
        login_user(admin_user)
        with pytest.raises(ValueError) as excinfo:
            update_stipend(stipend, update_data)

    assert "Invalid date format. Please use YYYY-MM-DD HH:MM:SS." in str(excinfo.value)

    # Check if the correct flash message was set
    with app.test_request_context():
        assert len(get_flashed_messages(category_filter=[FLASH_CATEGORY_ERROR])) == 1
        assert get_flashed_messages(category_filter=[FLASH_CATEGORY_ERROR])[0] == FLASH_MESSAGES["INVALID_DATE_FORMAT"]

def test_update_stipend_open_for_applications(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    update_data = {
        'open_for_applications': 'y',
    }

    with app.app_context(), app.test_request_context():
        login_user(admin_user)
        update_stipend(stipend, update_data)

    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
    assert updated_stipend.open_for_applications is True

    # Check if the correct flash message was set
    with app.test_request_context():
        assert len(get_flashed_messages(category_filter=[FLASH_CATEGORY_SUCCESS])) == 1
        assert get_flashed_messages(category_filter=[FLASH_CATEGORY_SUCCESS])[0] == FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"]

def test_delete_existing_stipend(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    with app.app_context(), app.test_request_context():
        login_user(admin_user)
        delete_stipend(stipend.id)

    deleted_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
    assert deleted_stipend is None

    # Check if the correct flash message was set
    with app.test_request_context():
        assert len(get_flashed_messages(category_filter=[FLASH_CATEGORY_SUCCESS])) == 1
        assert get_flashed_messages(category_filter=[FLASH_CATEGORY_SUCCESS])[0] == FLASH_MESSAGES["DELETE_STIPEND_SUCCESS"]

def test_delete_nonexistent_stipend(app, admin_user):
    with app.app_context(), app.test_request_context():
        login_user(admin_user)
        delete_stipend(9999)  # Assuming there's no stipend with ID 9999

        # Check if the correct flash message was set
        with app.test_request_context():
            assert len(get_flashed_messages(category_filter=[FLASH_CATEGORY_ERROR])) == 1
            assert get_flashed_messages(category_filter=[FLASH_CATEGORY_ERROR])[0] == FLASH_MESSAGES["STIPEND_NOT_FOUND"]

def test_get_stipend_by_valid_id(test_data, db_session, app):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    retrieved_stipend = get_stipend_by_id(stipend.id)
    assert retrieved_stipend is not None
    assert retrieved_stipend.name == test_data['name']

def test_get_stipend_by_invalid_id(app):
    retrieved_stipend = get_stipend_by_id(9999)  # Assuming there's no stipend with ID 9999
    assert retrieved_stipend is None

def test_get_all_stipends_with_multiple_entries(test_data, db_session, app):
    stipend1 = Stipend(**test_data)
    stipend2 = Stipend(name="Another Test Stipend", summary="Summary of another stipend")
    db_session.add(stipend1)
    db_session.add(stipend2)
    db_session.commit()

    all_stipends = get_all_stipends()
    assert len(all_stipends) == 2
    assert any(s.name == test_data['name'] for s in all_stipends)

def test_get_all_stipends_with_no_entries(app):
    all_stipends = get_all_stipends()
    assert len(all_stipends) == 0
