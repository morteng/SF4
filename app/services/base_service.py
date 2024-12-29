from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
import logging

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
    return wrapper

class BaseService:
    def __init__(self, model, audit_logger=None):
        self.model = model
        self.audit_logger = audit_logger

    @handle_errors
    def create(self, data, user_id):
        entity = self.model(**data)
        db.session.add(entity)
        db.session.commit()
        if self.audit_logger:
            self.audit_logger.log('create', entity.id, user_id)
        return entity

    @handle_errors
    def update(self, entity, data, user_id):
        for key, value in data.items():
            setattr(entity, key, value)
        db.session.commit()
        if self.audit_logger:
            self.audit_logger.log('update', entity.id, user_id)
        return entity

    @handle_errors
    def delete(self, id, user_id):
        entity = self.model.query.get(id)
        if entity:
            db.session.delete(entity)
            db.session.commit()
            if self.audit_logger:
                self.audit_logger.log('delete', id, user_id)

    def get_by_id(self, id):
        """Get entity by ID"""
        return self.model.query.get(id)

    def get_all(self):
        """Get all entities"""
        return self.model.query.all()
