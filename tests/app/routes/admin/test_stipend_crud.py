import pytest
from flask import url_for
from app.models.stipend import Stipend
from tests.conftest import extract_csrf_token

@pytest.fixture(scope='function')
def stipend_data():
    """Provide test data for stipends."""
    from datetime import datetime  # Add this import

    return {
        'name': 'Test Stipend',
        'summary': 'Test summary content.',
        'description': 'A test stipend for testing purposes.',
        'homepage_url': 'http://example.com',
        'application_procedure': 'Follow the steps outlined on the website.',
        'eligibility_criteria': 'Must be enrolled in a degree program.',
        'application_deadline': datetime(2024, 12, 31, 23, 59, 59),  # Change here
        'open_for_applications': True
    }

@pytest.fixture(scope='function')
def test_stipend(db_session, stipend_data):
    """Provide a test stipend for use in tests."""
    from datetime import datetime

    stipend = Stipend(
        name=stipend_data['name'],
        summary=stipend_data['summary'],
        description=stipend_data['description'],
        homepage_url=stipend_data['homepage_url'],
        application_procedure=stipend_data['application_procedure'],
        eligibility_criteria=stipend_data['eligibility_criteria'],
        application_deadline=datetime.strptime(stipend_data['application_deadline'], '%Y-%m-%d %H:%M:%S') if isinstance(stipend_data['application_deadline'], str) else stipend_data['application_deadline'],
        open_for_applications=stipend_data['open_for_applications']
    )
    db_session.add(stipend)
    db_session.commit()
    yield stipend

    # Teardown: Attempt to delete the stipend and rollback if an error occurs
    try:
        db_session.delete(stipend)
        db_session.commit()
    except Exception as e:
        print(f"Failed to delete test stipend during teardown: {e}")
        db_session.rollback()

def test_update_stipend_route(logged_in_admin, test_stipend, db_session):
    update_response = logged_in_admin.get(url_for('admin.stipend.update', id=test_stipend.id))
    assert update_response.status_code == 200

    csrf_token = extract_csrf_token(update_response.data)
    updated_data = {
        'name': 'Updated Stipend Name',
        'summary': 'Updated summary content.',
        'description': test_stipend.description,
        'homepage_url': test_stipend.homepage_url,
        'application_procedure': test_stipend.application_procedure,
        'eligibility_criteria': test_stipend.eligibility_criteria,
        'application_deadline': test_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') if hasattr(test_stipend.application_deadline, 'strftime') else test_stipend.application_deadline,
        'open_for_applications': False,  # Ensure this is set to False
        'csrf_token': csrf_token
    }
    
    print(f"Updated data being sent: {updated_data}")  # Add logging here
    
    response = logged_in_admin.post(url_for('admin.stipend.update', id=test_stipend.id), data=updated_data, follow_redirects=True)

    assert response.status_code == 200
    updated_stipend = db_session.get(Stipend, test_stipend.id)  # Use db_session.get to retrieve the stipend
    
    print(f"Updated stipend data: {updated_stipend.__dict__}")  # Add logging here
    
    assert updated_stipend.name == 'Updated Stipend Name'
    assert updated_stipend.summary == 'Updated summary content.'
    assert updated_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == test_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S')
    assert not updated_stipend.open_for_applications  # Ensure this is False
