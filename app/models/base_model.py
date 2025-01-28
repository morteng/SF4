from sqlalchemy.ext.declarative import declarative_base
from app.models.mixins import TimestampMixin, SoftDeleteMixin

Base = declarative_base()

class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    __abstract__ = True

    def save(self):
        from app.extensions import db
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
