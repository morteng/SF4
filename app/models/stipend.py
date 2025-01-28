from app.models.base_model import BaseModel
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.organization import Organization
from app.models.relationships import stipend_tag_association

class Stipend(BaseModel):
    __tablename__ = "stipends"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization_id = Column(Integer, ForeignKey('organization.id'))
    organization = relationship(Organization, back_populates='stipends')
    tags = relationship("Tag", secondary=stipend_tag_association, back_populates='stipends')

    def __repr__(self):
        return f"Stipend('{self.name}')"
