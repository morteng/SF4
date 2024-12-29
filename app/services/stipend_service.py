from app.models.stipend import Stipend
from app.services.base_service import BaseService

class StipendService(BaseService):
    def __init__(self):
        super().__init__(Stipend)

    def create_stipend(self, data, user_id=None):
        """Create a new stipend"""
        return self.create(data, user_id)

    def update_stipend(self, stipend_id, data, user_id=None):
        """Update an existing stipend"""
        return self.update(stipend_id, data, user_id)

    def delete_stipend(self, stipend_id, user_id=None):
        """Delete a stipend"""
        return self.delete(stipend_id, user_id)
