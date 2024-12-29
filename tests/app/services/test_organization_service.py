import pytest
from datetime import datetime
from app.models.organization import Organization
from app.services.organization_service import OrganizationService
from app.extensions import db
from app.constants import FlashMessages
from tests.conftest import BaseCRUDTest

class TestOrganizationService(BaseCRUDTest):
    service_class = OrganizationService
    model_class = Organization

    @pytest.fixture
    def test_data(self):
        return {
            'name': 'Test Organization',
            'description': 'This is a test organization.',
            'homepage_url': 'http://example.com/organization'
        }

    def test_search_organizations(self, db_session, app):
        with app.app_context():
            # Create test organizations
            org1 = Organization(name='Test Org 1', description='Desc 1')
            org2 = Organization(name='Another Org', description='Desc 2')
            db_session.add_all([org1, org2])
            db_session.commit()

            service = OrganizationService()
            results = service.search_organizations('Test')
            assert len(results) == 1
            assert results[0].name == 'Test Org 1'

    def test_create_organization_with_missing_name(self, test_data, db_session, app):
        with app.app_context():
            service = OrganizationService()
            invalid_data = test_data.copy()
            invalid_data['name'] = ''
            
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data)
            assert FlashMessages.REQUIRED_FIELD.format(field='name') in str(exc_info.value)

    def test_create_organization_with_missing_description(self, test_data, db_session, app):
        with app.app_context():
            service = OrganizationService()
            invalid_data = test_data.copy()
            invalid_data['description'] = ''
            
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data)
            assert FlashMessages.REQUIRED_FIELD.format(field='description') in str(exc_info.value)

