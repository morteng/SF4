from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from wtforms import ValidationError
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
            raise ValueError("A database error occurred. Please try again later.")
        except ValidationError as e:
            db.session.rollback()
            logger.error(f"Validation error in {func.__name__}: {str(e)}")
            raise ValueError(str(e))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise ValueError("An unexpected error occurred. Please try again later.")
    return wrapper

class BaseService:
    def __init__(self, model, audit_logger=None):
        self.model = model
        self.audit_logger = audit_logger
        self.soft_delete_enabled = hasattr(model, 'is_deleted')
        self.validation_rules = {}

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
        """Create a new entity with validation and audit logging"""
        self.validate_create(data)
        entity = self.model(**data)
        db.session.add(entity)
        db.session.commit()
        
        self._log_audit('create', entity, user_id=user_id, after=entity.to_dict())
        return entity

    def validate(self, data):
        """Validate data against defined rules"""
        for field, rules in self.validation_rules.items():
            if rules.get('required') and not data.get(field):
                raise ValidationError(f"{field} is required")
            if rules.get('max_length') and len(str(data.get(field))) > rules['max_length']:
                raise ValidationError(f"{field} exceeds maximum length")
            if rules.get('choices') and data.get(field) not in rules['choices']:
                raise ValidationError(f"{field} must be one of {rules['choices']}")

    def validate_create(self, data):
        """Validate data before creation"""
        self.validate(data)
        
    def validate_update(self, data):
        """Validate data before update"""
        self.validate(data)

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
        
        self._log_audit('update', entity, user_id=user_id, before=before, after=entity.to_dict())
        return entity

    @handle_errors
    def delete(self, id, user_id=None):
        """Enhanced delete with soft delete support"""
        entity = self.get_by_id(id)
        
        if self.soft_delete_enabled:
            return self.soft_delete(id, user_id)
            
        db.session.delete(entity)
        db.session.commit()
        
        self._log_audit('delete', entity, user_id=user_id, before=entity.to_dict())
        return entity

    def get_active(self):
        """Get only active (non-deleted) entities"""
        if self.soft_delete_enabled:
            return self.model.query.filter_by(is_deleted=False)
        return self.model.query
        
    def get_deleted(self):
        """Get only deleted entities"""
        if self.soft_delete_enabled:
            return self.model.query.filter_by(is_deleted=True)
        raise ValueError("Model does not support soft delete")
        
    def bulk_restore(self, ids, user_id=None):
        """Restore multiple soft deleted entities"""
        if not self.soft_delete_enabled:
            raise ValueError("Model does not support soft delete")
            
        entities = self.model.query.filter(self.model.id.in_(ids)).all()
        for entity in entities:
            entity.is_deleted = False
            self._log_audit('restore', entity, user_id=user_id)
        db.session.commit()
        return entities

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

    def _log_audit(self, action, entity, user_id=None, before=None, after=None):
        """Centralized audit logging"""
        if self.audit_logger:
            self.audit_logger.log(
                action=action,
                object_type=self.model.__name__,
                object_id=entity.id,
                user_id=user_id,
                before=before,
                after=after or entity.to_dict()
            )
