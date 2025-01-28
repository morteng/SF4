from datetime import datetime
from sqlalchemy import Column, Boolean, DateTime

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False, index=True)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    @classmethod
    def query_with_deleted(cls):
        return cls.query()

    @classmethod
    def query_deleted(cls):
        return cls.query().filter(cls.is_deleted == True)

    @classmethod
    def query_undeleted(cls):
        return cls.query().filter(cls.is_deleted == False)
