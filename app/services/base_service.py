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
        except ValidationError as e:
            db.session.rollback()
            logger.error(f"Validation error in {func.__name__}: {str(e)}")
            raise ValueError(FlashMessages.CRUD_VALIDATION_ERROR.format(errors=e.messages))
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise ValueError(FlashMessages.DATABASE_ERROR)
        except ValueError as e:
            db.session.rollback()
            logger.error(f"Value error in {func.__name__}: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise ValueError(FlashMessages.CRUD_OPERATION_ERROR.format(error=str(e)))
    return wrapper

class BaseService:
    def __init__(self, model, audit_logger=None):
        self.model = model
        self.audit_logger = audit_logger
        self.soft_delete_enabled = hasattr(model, 'is_deleted')
        self.validation_rules = {}
        self.pre_create_hooks = []
        self.post_create_hooks = []
        self.pre_update_hooks = [] 
        self.post_update_hooks = []
        self.pre_delete_hooks = []
        self.post_delete_hooks = []
        self.pre_validation_hooks = []
        self.post_validation_hooks = []

    def add_pre_create_hook(self, hook):
        self.pre_create_hooks.append(hook)
        
    def add_post_create_hook(self, hook):
        self.post_create_hooks.append(hook)
        
    def add_pre_update_hook(self, hook):
        self.pre_update_hooks.append(hook)
        
    def add_post_update_hook(self, hook):
        self.post_update_hooks.append(hook)
        
    def add_pre_delete_hook(self, hook):
        self.pre_delete_hooks.append(hook)
        
    def add_post_delete_hook(self, hook):
        self.post_delete_hooks.append(hook)

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
        try:
            # Run pre-create hooks
            for hook in self.pre_create_hooks:
                data = hook(data)
                
            self.validate_create(data)
            entity = self.model(**data)
            db.session.add(entity)
            db.session.commit()
            
            # Run post-create hooks
            for hook in self.post_create_hooks:
                hook(entity)
            
            self._log_audit('create', entity, user_id=user_id, after=entity.to_dict())
            return entity
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise ValueError(f"Failed to create {self.model.__name__}: {str(e)}")

    def validate(self, data):
        """Enhanced validation with hooks"""
        errors = {}
        
        # Run pre-validation hooks
        for hook in self.pre_validation_hooks:
            try:
                data = hook(data)
            except ValidationError as e:
                errors.update({field: str(e) for field in e.messages})
            
        # Core validation
        for field, rules in self.validation_rules.items():
            try:
                value = data.get(field)
                
                if rules.get('required') and not value:
                    raise ValidationError(FlashMessages.MISSING_REQUIRED_FIELD.format(field=field))
                    
                if rules.get('max_length') and len(str(value)) > rules['max_length']:
                    raise ValidationError(FlashMessages.NAME_LENGTH)
                    
                if rules.get('choices') and value not in rules['choices']:
                    raise ValidationError(f"{field} must be one of {rules['choices']}")
                    
                if rules.get('type') and not isinstance(value, rules['type']):
                    raise ValidationError(f"{field} must be of type {rules['type'].__name__}")
                    
            except ValidationError as e:
                errors[field] = str(e)
            
        # Run post-validation hooks
        for hook in self.post_validation_hooks:
            try:
                hook(data)
            except ValidationError as e:
                errors.update({field: str(e) for field in e.messages})
            
        if errors:
            raise ValidationError(FlashMessages.CRUD_VALIDATION_ERROR.format(errors=errors))

    def validate_create(self, data):
        """Validate data before creation"""
        if not data:
            raise ValidationError(FlashMessages.CRUD_VALIDATION_ERROR.format(errors="No data provided"))
        self.validate(data)
        
    def validate_update(self, data):
        """Validate data before update"""
        if not data:
            raise ValidationError(FlashMessages.CRUD_VALIDATION_ERROR.format(errors="No data provided"))
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
        """Enhanced audit logging with IP and endpoint tracking"""
        from flask import request
        if self.audit_logger:
            self.audit_logger.log(
                action=action,
                object_type=self.model.__name__,
                object_id=entity.id,
                user_id=user_id,
                before=before,
                after=after or entity.to_dict(),
                ip_address=request.remote_addr if request else '127.0.0.1',
                endpoint=request.endpoint if request else 'unknown',
                http_method=request.method if request else 'UNKNOWN',
                user_agent=request.headers.get('User-Agent') if request else None
            )
