from sqlalchemy.ext.declarative import declarative_base
from app.models.mixins import TimestampMixin, SoftDeleteMixin
from app.extensions import db

Base = declarative_base()

class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """Base model class that other models inherit from."""
    __abstract__ = True

    def delete(self):
        db.session.delete(self)
        db.session.commit()
