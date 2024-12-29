import pytest
from app.models.organization import Organization
from app.services.organization_service import OrganizationService
from app.extensions import db

@pytest.fixture(scope='function')
def org_service():
    return OrganizationService()

@pytest.fixture(scope='function')
def organization_data():
    return {
        'name': 'Test Organization',
        'description': 'This is a test organization.',
        'homepage_url': 'http://example.com/organization'
    }

@pytest.fixture(scope='function')
def test_organization(db_session, organization_data):
    """Provide a test organization."""
    organization = Organization(**organization_data)
    db_session.add(organization)
    db_session.commit()
    yield organization
    db_session.delete(organization)
    db_session.commit()

def test_get_all_organizations(db_session, test_organization, org_service):
    organizations = org_service.get_all()
    assert len(organizations) >= 1
    assert test_organization in organizations

def test_delete_organization(db_session, test_organization, org_service):
    org_service.delete(test_organization)
    db_session.expire_all()
    organization = db_session.get(Organization, test_organization.id)
    assert organization is None

def test_create_organization(db_session, organization_data, org_service):
    organization = org_service.create(organization_data)
    assert organization is not None
    assert organization.name == organization_data['name']
    assert organization.description == organization_data['description']
    assert organization.homepage_url == organization_data['homepage_url']

def test_get_organization_by_id(db_session, test_organization, org_service):
    organization = org_service.get_by_id(test_organization.id)
    assert organization is not None
    assert organization.name == test_organization.name
    assert organization.description == test_organization.description
    assert organization.homepage_url == test_organization.homepage_url

def test_update_organization(db_session, test_organization, org_service):
    updated_data = {
        'name': 'Updated Organization',
        'description': 'This is an updated organization.',
        'homepage_url': 'http://example.com/updated-organization'
    }
    updated_organization = org_service.update(test_organization, updated_data)
    assert updated_organization is not None
    assert updated_organization.name == updated_data['name']
    assert updated_organization.description == updated_data['description']
    assert updated_organization.homepage_url == updated_data['homepage_url']

def test_update_organization_with_invalid_id(db_session, org_service):
    non_existent_id = 9999
    updated_data = {
        'name': 'Updated Organization',
        'description': 'This is an updated organization.',
        'homepage_url': 'http://example.com/updated-organization'
    }
    organization = db_session.get(Organization, non_existent_id)
    assert organization is None

    with pytest.raises(ValueError) as exc_info:
        org_service.update(organization, updated_data)
    assert "Organization not found" in str(exc_info.value)

