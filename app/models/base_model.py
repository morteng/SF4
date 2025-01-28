from sqlalchemy.ext.declarative import declarative_base
from app.models.mixins import TimestampMixin, SoftDeleteMixin
from app.extensions import db

Base = declarative_base()

class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """Base model class that other models inherit from."""
    __abstract__ = True
    __tablename__ = 'base_model'

    def save(self):
        """Save the model instance to the database."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Soft delete the model instance."""
        db.session.delete(self)
        db.session.commit()
