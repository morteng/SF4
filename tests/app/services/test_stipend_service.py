import pytest
from app.services.stipend_service import create_stipend, get_all_stipends, delete_stipend, update_stipend, get_stipend_by_id
from app.models.stipend import Stipend
from datetime import datetime, timedelta

@pytest.fixture(scope='function')
def test_data():
    return {
        'name': 'Test Stipend',
        'summary': 'This is a test stipend.',
        'description': 'Detailed description of the test stipend.',
        'homepage_url': 'http://example.com/test-stipend',
        'application_procedure': 'Apply online at http://example.com/apply',
        'eligibility_criteria': 'Open to all students.',
        'application_deadline': datetime.now(),
        'open_for_applications': True
    }

@pytest.fixture(scope='function', autouse=True)
def clean_stipends(db_session):
    yield
    db_session.query(Stipend).delete()
    db_session.commit()

def test_create_stipend(test_data, db_session):
    # Create a stipend using the service function with the provided session
    stipend = Stipend(**test_data)
    new_stipend = create_stipend(stipend)

    # Assert that the stipend was created successfully
    assert new_stipend is not None

    # Retrieve all stipends from the database and check if the new stipend is in the list
    stipends = get_all_stipends()
    assert len(stipends) == 1
    assert stipends[0].name == test_data['name']
    assert stipends[0].summary == test_data['summary']
    assert stipends[0].description == test_data['description']
    assert stipends[0].homepage_url == test_data['homepage_url']
    assert stipends[0].application_procedure == test_data['application_procedure']
    assert stipends[0].eligibility_criteria == test_data['eligibility_criteria']

    # Convert the application_deadline to a string before comparison with a tolerance
    deadline_tolerance = timedelta(seconds=1)
    assert abs(stipends[0].application_deadline - test_data['application_deadline']) < deadline_tolerance
    assert stipends[0].open_for_applications == test_data['open_for_applications']

def test_create_stipend_duplicate_name(test_data, db_session):
    # Create a stipend using the service function with the provided session
    stipend = Stipend(**test_data)
    new_stipend = create_stipend(stipend)

    # Assert that the stipend was created successfully
    assert new_stipend is not None

    # Attempt to create another stipend with the same name
    duplicate_stipend = Stipend(**test_data)
    result = create_stipend(duplicate_stipend)

    # Assert that the creation failed due to duplicate name
    assert result is None

def test_create_stipend_invalid_deadline(test_data, db_session):
    # Modify test data with an invalid deadline
    test_data['application_deadline'] = "invalid-date"
    stipend = Stipend(**test_data)
    new_stipend = create_stipend(stipend)

    # Assert that the stipend was created successfully with application_deadline set to None
    assert new_stipend is not None
    assert new_stipend.application_deadline is None

def test_update_stipend(test_data, db_session):
    # Create a stipend using the service function with the provided session
    stipend = Stipend(**test_data)
    new_stipend = create_stipend(stipend)

    # Assert that the stipend was created successfully
    assert new_stipend is not None

    # Update the stipend
    updated_data = {
        'name': 'Updated Test Stipend',
        'summary': 'Updated summary',
        'description': 'Updated description',
        'homepage_url': 'http://example.com/updated-stipend',
        'application_procedure': 'Updated application procedure',
        'eligibility_criteria': 'Updated eligibility criteria',
        'application_deadline': datetime.now() + timedelta(days=1),
        'open_for_applications': False
    }
    for key, value in updated_data.items():
        setattr(stipend, key, value)
    update_stipend(stipend)

    # Retrieve the updated stipend from the database and check if it was updated successfully
    updated_stipend = get_stipend_by_id(stipend.id)
    assert updated_stipend.name == updated_data['name']
    assert updated_stipend.summary == updated_data['summary']
    assert updated_stipend.description == updated_data['description']
    assert updated_stipend.homepage_url == updated_data['homepage_url']
    assert updated_stipend.application_procedure == updated_data['application_procedure']
    assert updated_stipend.eligibility_criteria == updated_data['eligibility_criteria']

    # Convert the application_deadline to a string before comparison with a tolerance
    deadline_tolerance = timedelta(seconds=1)
    assert abs(updated_stipend.application_deadline - updated_data['application_deadline']) < deadline_tolerance
    assert updated_stipend.open_for_applications == updated_data['open_for_applications']

def test_delete_stipend(test_data, db_session):
    # Create a stipend using the service function with the provided session
    stipend = Stipend(**test_data)
    new_stipend = create_stipend(stipend)

    # Assert that the stipend was created successfully
    assert new_stipend is not None

    # Delete the stipend
    delete_stipend(new_stipend)

    # Retrieve all stipends from the database and check if it was deleted successfully
    stipends = get_all_stipends()
    assert len(stipends) == 0
