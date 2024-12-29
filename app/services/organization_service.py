from app.models.organization import Organization
from app.services.base_service import BaseService

class OrganizationService(BaseService):
    def __init__(self):
        super().__init__(Organization)
