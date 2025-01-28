from sqlalchemy import Column, DateTime, Integer, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime
import logging

Base = declarative_base()

class Base(Base):
    __abstract__ = True

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
