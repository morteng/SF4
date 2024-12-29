from sqlalchemy.exc import SQLAlchemyError
from wtforms.validators import ValidationError
from app.extensions import db

class BaseService:
    """Base service class providing common CRUD operations"""
    
    def __init__(self, model, audit_logger=None):
        self.model = model
        self.audit_logger = audit_logger
        
    def _log_operation(self, action, object_id, details=None):
        if self.audit_logger:
            self.audit_logger.log(action, self.model.__name__, object_id, details)
            
    def create(self, data):
        """Create a new entity with audit logging"""
        try:
            entity = self.model(**data)
            db.session.add(entity)
            db.session.commit()
            self._log_operation('create', entity.id, 'Entity created')
            return entity
        except Exception as e:
            db.session.rollback()
            raise

    def create(self, data):
        """Create a new entity"""
        try:
            entity = self.model(**data)
            db.session.add(entity)
            db.session.commit()
            if self.audit_logger:
                self._log_operation('create', entity.id, 'Entity created')
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            import logging
            logging.error(f"Error creating entity: {str(e)}", exc_info=True)
            raise ValidationError(f"Error creating entity: {str(e)}")

    def update(self, entity, data):
        """Update an existing entity"""
        try:
            for key, value in data.items():
                setattr(entity, key, value)
            db.session.commit()
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValidationError(f"Error updating entity: {str(e)}")

    def delete(self, entity):
        """Delete an entity"""
        try:
            db.session.delete(entity)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValidationError(f"Error deleting entity: {str(e)}")

    def get_by_id(self, id):
        """Get entity by ID"""
        return self.model.query.get(id)

    def get_all(self):
        """Get all entities"""
        return self.model.query
