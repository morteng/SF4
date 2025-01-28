from typing import Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from app.models.audit_log import AuditLog

class BaseService:
    def __init__(self, model):
        self.model = model

    def create(self, data: Dict[str, Any]) -> None:
        try:
            self.model.create(**data)
        except SQLAlchemyError as e:
            raise e

    def get(self, id: int) -> 'BaseService.model':
        return self.model.query.get(id)

    def delete(self, id: int) -> None:
        try:
            entity = self.get(id)
            if entity:
                entity.delete()
        except SQLAlchemyError as e:
            raise e
