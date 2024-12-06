import pytest
from app.services.stipend_service import create_stipend, get_all_stipends
from app.models.stipend import Stipend
from datetime import datetime

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

def test_create_stipend(test_data, session):
    # Create a stipend using the service function
    new_stipend = create_stipend(test_data)

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
    # Convert the application_deadline to a string before comparison
    assert stipends[0].application_deadline.strftime('%Y-%m-%d %H:%M:%S') == test_data['application_deadline'].strftime('%Y-%m-%d %H:%M:%S')

    # Clean up: delete the created stipend
    session.delete(new_stipend)
    session.commit()
