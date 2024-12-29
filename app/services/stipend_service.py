from app.models.stipend import Stipend
from app.services.base_service import BaseService

class StipendService(BaseService):
    def __init__(self):
        super().__init__(Stipend)
