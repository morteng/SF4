from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
import logging
from app.constants import FlashMessages, FlashCategory

logger = logging.getLogger(__name__)

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper

class BaseService:
    def __init__(self, model, audit_logger=None):
        self.model = model
        self.audit_logger = audit_logger

    @handle_errors
    def get_by_id(self, id):
        """Get entity by ID or raise 404"""
        entity = self.model.query.get(id)
        if not entity:
            raise ValueError(FlashMessages.NOT_FOUND.format(entity_name=self.model.__name__))
        return entity

    @handle_errors
    def get_all(self):
        """Get all entities with pagination support"""
        return self.model.query

    @handle_errors
    def create(self, data, user_id=None):
        """Create a new entity"""
        entity = self.model(**data)
        db.session.add(entity)
        db.session.commit()
        
        if self.audit_logger:
            self.audit_logger.log(
                action='create',
                object_type=self.model.__name__,
                object_id=entity.id,
                user_id=user_id,
                after=entity.to_dict()
            )
        return entity

    @handle_errors
    def update(self, id, data, user_id=None):
        """Update an existing entity with validation and audit logging"""
        entity = self.get_by_id(id)
        
        if hasattr(self, '_validate_update_data'):
            self._validate_update_data(data)
            
        before = entity.to_dict()
        for key, value in data.items():
            setattr(entity, key, value)
        db.session.commit()
        
        self._log_audit('update', entity, user_id=user_id, before=before)
        return entity

    @handle_errors
    def delete(self, id, user_id=None):
        """Delete an entity"""
        entity = self.get_by_id(id)
        db.session.delete(entity)
        db.session.commit()
        
        self._log_audit('delete', entity, user_id=user_id, before=entity.to_dict())
        return entity

    def soft_delete(self, id, user_id=None):
        """Soft delete implementation"""
        entity = self.get_by_id(id)
        if hasattr(entity, 'is_deleted'):
            setattr(entity, 'is_deleted', True)
            db.session.commit()
            self._log_audit('soft_delete', entity, user_id=user_id)
            return entity
        raise ValueError("Model does not support soft delete")

    def restore(self, id, user_id=None):
        """Restore soft deleted entity"""
        entity = self.get_by_id(id)
        if hasattr(entity, 'is_deleted'):
            setattr(entity, 'is_deleted', False)
            db.session.commit()
            self._log_audit('restore', entity, user_id=user_id)
            return entity
        raise ValueError("Model does not support restore")
