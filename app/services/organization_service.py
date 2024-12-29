from app.models.organization import Organization
from app.services.base_service import BaseService

class OrganizationService(BaseService):
    def __init__(self):
        super().__init__(Organization)

    def get_all_organizations(self):
        """Get all organizations"""
        return self.model.query.all()

    def create_organization(self, data, user_id=None):
        """Create a new organization"""
        return self.create(data, user_id)

    def update_organization(self, org_id, data, user_id=None):
        """Update an existing organization"""
        return self.update(org_id, data, user_id)

    def delete_organization(self, org_id, user_id=None):
        """Delete an organization"""
        return self.delete(org_id, user_id)

    def get_organization_by_id(self, org_id):
        """Get a single organization by ID"""
        return self.get_by_id(org_id)
