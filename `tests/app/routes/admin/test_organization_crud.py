import pytest
from flask import url_for, get_flashed_messages
from app.models.organization import Organization
from tests.conftest import extract_csrf_token

@pytest.fixture(scope='function')
def organization_data():
    return {
        'name': 'Test Organization',
        'description': 'A test organization for testing purposes.',
        'homepage_url': 'http://example.com'
    }

@pytest.fixture(scope='function')
def test_organization(db_session, organization_data):
    organization = Organization(**organization_data)
    db_session.add(organization)
    db_session.commit()
    yield organization

    # Teardown: Attempt to delete the organization and rollback if an error occurs
    try:
        db_session.delete(organization)
        db_session.commit()
    except Exception as e:
        print(f"Failed to delete test organization during teardown: {e}")
        db_session.rollback()

def test_create_organization_route(logged_in_admin, organization_data):
    with logged_in_admin.application.app_context():
        # Fetch CSRF token from the form page
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        response = logged_in_admin.post(url_for('admin.organization.create'), data={
            'name': organization_data['name'],
            'description': organization_data['description'],
            'homepage_url': organization_data['homepage_url'],
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200
        new_organization = db_session.query(Organization).filter_by(name=organization_data['name']).first()
        assert new_organization is not None

def test_create_organization_route_with_invalid_data(logged_in_admin, organization_data):
    with logged_in_admin.application.app_context():
        # Fetch CSRF token from the form page
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        invalid_data = {
            'name': '',  # Intentionally empty
            'description': organization_data['description'],
            'homepage_url': organization_data['homepage_url'],
            'csrf_token': csrf_token
        }
        
        response = logged_in_admin.post(url_for('admin.organization.create'), data=invalid_data)
        
        assert response.status_code == 200

        form = OrganizationForm(data=invalid_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
            
        # Check that the organization was not created
        new_organization = db_session.query(Organization).filter_by(name=invalid_data['name']).first()
        assert new_organization is None

def test_delete_organization_route(logged_in_admin, test_organization, db_session):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.organization.delete', id=test_organization.id))
        
        assert response.status_code == 302
        flash_message = list(filter(lambda x: 'deleted' in x, get_flashed_messages()))
        assert len(flash_message) > 0

        # Ensure the organization is no longer in the session after deleting
        db_session.expire_all()
        updated_organization = db_session.get(Organization, test_organization.id)
        assert updated_organization is None

def test_delete_nonexistent_organization_route(logged_in_admin):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.post(url_for('admin.organization.delete', id=9999))
        
        assert response.status_code == 302
        flash_message = list(filter(lambda x: 'not found' in x, get_flashed_messages()))
        assert len(flash_message) > 0

def test_update_organization_route(logged_in_admin, test_organization, db_session):
    with logged_in_admin.application.app_context():
        update_response = logged_in_admin.get(url_for('admin.organization.update', id=test_organization.id))
        assert update_response.status_code == 200

        csrf_token = extract_csrf_token(update_response.data)
        updated_data = {
            'name': 'Updated Organization Name',
            'description': test_organization.description,
            'homepage_url': test_organization.homepage_url,
            'csrf_token': csrf_token
        }
        response = logged_in_admin.post(url_for('admin.organization.update', id=test_organization.id), data=updated_data, follow_redirects=True)

        assert response.status_code == 200
        updated_organization = db_session.get(Organization, test_organization.id)
        assert updated_organization.name == 'Updated Organization Name'

def test_create_organization_route_with_duplicate_name(logged_in_admin, test_organization, organization_data):
    with logged_in_admin.application.app_context():
        # Fetch CSRF token from the form page
        response = logged_in_admin.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(response.data)

        duplicate_data = {
            'name': test_organization.name,
            'description': "Duplicate description.",
            'homepage_url': "http://example.com/duplicate",
            'csrf_token': csrf_token
        }
        
        response = logged_in_admin.post(url_for('admin.organization.create'), data=duplicate_data)
        
        assert response.status_code == 200

        form = OrganizationForm(data=duplicate_data)
        if not form.validate():
            for field, errors in form.errors.items():
                print(f"Field {field} errors: {errors}")
            
        # Check that the organization was not created
        new_organization = db_session.query(Organization).filter_by(name=duplicate_data['name']).first()
        assert new_organization.id == test_organization.id  # Ensure it's the same organization

def test_create_organization_route_with_csrf_token(logged_in_admin, organization_data):
    with logged_in_admin.application.app_context():
        response = logged_in_admin.get(url_for('admin.organization.create'))
        assert response.status_code == 200
        csrf_token = extract_csrf_token(response.data)
        assert csrf_token is not None
