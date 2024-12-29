from app.models.stipend import Stipend
from app.services.base_service import BaseService

class StipendService(BaseService):
    def __init__(self):
        super().__init__(Stipend)

    def create(self, data, user_id=None):
        """Create a new stipend"""
        return super().create(data, user_id)

    def update(self, entity_id, data, user_id=None):
        """Update an existing stipend"""
        return super().update(entity_id, data, user_id)

    def delete(self, entity_id, user_id=None):
        """Delete a stipend"""
        return super().delete(entity_id, user_id)
