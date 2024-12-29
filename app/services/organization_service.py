from app.models.organization import Organization
from app.services.base_service import BaseService
from app.constants import FlashMessages

class OrganizationService(BaseService):
    def __init__(self):
        super().__init__(Organization)

    def search_organizations(self, query):
        """Search organizations by name"""
        return self.model.query.filter(self.model.name.ilike(f"%{query}%")).all()

    def _validate_create_data(self, data):
        """Validate organization data before creation"""
        self._validate_organization_data(data)

    def _validate_update_data(self, data):
        """Validate organization data before update"""
        self._validate_organization_data(data)

    def _validate_organization_data(self, data):
        """Common organization data validation"""
        if not data.get('name'):
            raise ValueError(FlashMessages.REQUIRED_FIELD.format(field='name'))
        if not data.get('description'):
            raise ValueError(FlashMessages.REQUIRED_FIELD.format(field='description'))
