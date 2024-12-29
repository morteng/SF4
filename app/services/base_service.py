from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db

class BaseService:
    def __init__(self, model, audit_logger=None):
        self.model = model
        self.audit_logger = audit_logger

    def create(self, data, user_id):
        try:
            entity = self.model(**data)
            db.session.add(entity)
            db.session.commit()
            if self.audit_logger:
                self.audit_logger.log('create', entity.id, user_id)
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    def update(self, entity, data, user_id):
        try:
            for key, value in data.items():
                setattr(entity, key, value)
            db.session.commit()
            if self.audit_logger:
                self.audit_logger.log('update', entity.id, user_id)
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    def delete(self, id, user_id):
        try:
            entity = self.model.query.get(id)
            if entity:
                db.session.delete(entity)
                db.session.commit()
                if self.audit_logger:
                    self.audit_logger.log('delete', id, user_id)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise

    def get_by_id(self, id):
        """Get entity by ID"""
        return self.model.query.get(id)

    def get_all(self):
        """Get all entities"""
        return self.model.query.all()
