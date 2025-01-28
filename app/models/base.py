from sqlalchemy import Column, DateTime, Integer, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime
import logging

# Create the declarative base
Base = declarative_base()

class BaseMixin:
    """Base mixin class that provides common columns and methods"""
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)

    def save(self, session):
        """Save the current instance to the database."""
        try:
            session.add(self)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logging.error(f"Error saving {self.__class__.__name__}: {str(e)}")
            raise e

    def delete(self, session):
        """Delete the current instance from the database."""
        try:
            session.delete(self)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logging.error(f"Error deleting {self.__class__.__name__}: {str(e)}")
            raise e

    def to_dict(self):
        """Return a dictionary representation of the model."""
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

class BaseModel(Base, BaseMixin):
    """Base class for all models that uses the declarative base and mixin"""
    pass
