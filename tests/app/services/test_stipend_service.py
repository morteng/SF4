import pytest
from app.models.stipend import Stipend
from app.services.stipend_service import create_stipend, update_stipend, delete_stipend
from datetime import datetime

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

def test_create_stipend(test_data, db_session):
    stipend = Stipend(**test_data)

    new_stipend = create_stipend(stipend)
    
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

def test_create_stipend_with_invalid_application_deadline_format(test_data, db_session):
    # Modify test data with an invalid application_deadline format
    test_data['application_deadline'] = '2023-13-32 99:99:99'
    stipend = Stipend(**test_data)
    new_stipend = create_stipend(stipend)

    # Assert that the stipend was created successfully with application_deadline set to None
    assert new_stipend is not None
    assert new_stipend.application_deadline is None

def test_update_stipend(test_data, db_session):
    stipend = Stipend(**test_data)
    new_stipend = create_stipend(stipend)

    # Check if the stipend was created successfully
    assert new_stipend is not None

    updated_data = {
        'name': test_data['name'],
        'summary': "Updated summary.",
        'description': "Updated description.",
        'homepage_url': "http://example.com/updated-stipend",
        'application_procedure': "Apply online at example.com/updated",
        'eligibility_criteria': "Open to all updated students",
        'application_deadline': datetime.strptime('2024-12-31 23:59:59', '%Y-%m-%d %H:%M:%S'),
        'open_for_applications': True
    }

    response = update_stipend(new_stipend, updated_data)

    # Check if the stipend was updated successfully
    assert response is not None
    assert response.name == updated_data['name']
    assert response.summary == "Updated summary."
    assert response.description == "Updated description."
    assert response.homepage_url == "http://example.com/updated-stipend"
    assert response.application_procedure == "Apply online at example.com/updated"
    assert response.eligibility_criteria == "Open to all updated students"
    assert response.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2024-12-31 23:59:59'
    assert response.open_for_applications is True

def test_update_stipend_with_invalid_application_deadline_format(test_data, db_session):
    stipend = Stipend(**test_data)
    new_stipend = create_stipend(stipend)

    # Check if the stipend was created successfully
    assert new_stipend is not None

    updated_data = {
        'name': test_data['name'],
        'summary': "Updated summary.",
        'description': "Updated description.",
        'homepage_url': "http://example.com/updated-stipend",
        'application_procedure': "Apply online at example.com/updated",
        'eligibility_criteria': "Open to all updated students",
        'application_deadline': '2023-13-32 99:99:99',
        'open_for_applications': True
    }

    response = update_stipend(new_stipend, updated_data)

    # Check if the stipend was updated in the database with application_deadline as None
    assert response.application_deadline is None

def test_update_stipend_with_database_error(test_data, db_session, monkeypatch):
    stipend = Stipend(**test_data)
    new_stipend = create_stipend(stipend)

    # Check if the stipend was created successfully
    assert new_stipend is not None

    updated_data = {
        'name': test_data['name'],
        'summary': "Updated summary.",
        'description': "Updated description.",
        'homepage_url': "http://example.com/updated-stipend",
        'application_procedure': "Apply online at example.com/updated",
        'eligibility_criteria': "Open to all updated students",
        'application_deadline': datetime.strptime('2024-12-31 23:59:59', '%Y-%m-%d %H:%M:%S'),
        'open_for_applications': True
    }

    # Mock a database error during commit
    def mock_commit(*args, **kwargs):
        raise Exception("Database error")
        
    monkeypatch.setattr(db_session, 'commit', mock_commit)
    
    response = update_stipend(new_stipend, updated_data)

    # Check if the stipend was not updated in the database
    assert response.summary != "Updated summary."

def test_delete_stipend(test_data, db_session):
    stipend = Stipend(**test_data)
    new_stipend = create_stipend(stipend)

    # Check if the stipend was created successfully
    assert new_stipend is not None

    response = delete_stipend(new_stipend.id)

    # Check if the stipend was deleted from the database
    stipend = db_session.get(Stipend, new_stipend.id)
    assert stipend is None

def test_delete_stipend_with_database_error(test_data, db_session, monkeypatch):
    stipend = Stipend(**test_data)
    new_stipend = create_stipend(stipend)

    # Check if the stipend was created successfully
    assert new_stipend is not None

    # Mock a database error during commit
    def mock_commit(*args, **kwargs):
        raise Exception("Database error")
        
    monkeypatch.setattr(db_session, 'commit', mock_commit)
    
    response = delete_stipend(new_stipend.id)

    # Check if the stipend was not deleted from the database
    stipend = db_session.get(Stipend, new_stipend.id)
    assert stipend is not None
