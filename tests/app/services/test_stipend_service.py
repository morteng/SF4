import pytest
from app.services.stipend_service import create_stipend, get_all_stipends, delete_stipend
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
        # Convert datetime object to string
        'application_deadline': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'open_for_applications': True
    }

# ensure we test with both a valid application deadline, an invalid application deadline, and a null application deadline. if the application deadline is invalid then it should be set to null. if the application deadline is null then it should be set to null. if the application deadline is valid then it should be set to the provided value. AI!


def test_create_stipend(test_data, session):
    # Clean up any existing stipends before the test
    existing_stipends = get_all_stipends()
    for stipend in existing_stipends:
        delete_stipend(stipend, session)
    session.commit()

    # Create a stipend using the service function with the provided session
    new_stipend = create_stipend(test_data, session)

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
    deadline_tolerance = timedelta(seconds=1)  # Allow up to 1 second difference
    assert abs((stipends[0].application_deadline - datetime.strptime(test_data['application_deadline'], '%Y-%m-%d %H:%M:%S')).total_seconds()) < deadline_tolerance.total_seconds()

    # Clean up: delete the created stipend using the provided session
    delete_stipend(new_stipend, session)
    session.commit()
