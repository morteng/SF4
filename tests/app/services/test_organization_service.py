import pytest
from app.models import Organization
from app.services.organization_service import OrganizationService
from app import db
from app.forms.admin_forms import OrganizationForm

@pytest.fixture
def organization_service():
    return OrganizationService()

@pytest.fixture
def test_data():
    return {
        'name': 'Test Organization',
        'description': 'Test Description'
    }

def test_create_organization(organization_service, test_data, db_session):
    # Test valid organization creation
    org = organization_service.create(test_data)
    db_session.commit()
    assert org.id is not None
    assert org.name == test_data['name']
    assert org.description == test_data['description']

def test_update_organization(organization_service, test_data, db_session):
    # Test organization update
    org = organization_service.create(test_data)
    db_session.commit()
    updated_data = {
        'name': 'Updated Name',
        'description': 'Updated Description'
    }
    updated_org = organization_service.update(org, updated_data)
    db_session.commit()
    assert updated_org.name == updated_data['name']
    assert updated_org.description == updated_data['description']

def test_delete_organization(organization_service, test_data, db_session):
    # Test organization deletion
    org = organization_service.create(test_data)
    db_session.commit()
    organization_service.delete(org)
    db_session.commit()
    assert organization_service.get(org.id) is None
