from app.models.organization import Organization
from app.services.base_service import BaseService

class OrganizationService(BaseService):
    def __init__(self):
        super().__init__(Organization)

    def search_organizations(self, query):
        """Search organizations by name"""
        return self.model.query.filter(self.model.name.ilike(f"%{query}%")).all()
