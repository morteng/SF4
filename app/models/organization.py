from app.models.base import Base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

class Organization(Base):
    __tablename__ = 'organization'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    website = Column(String(512))
    
    stipends = relationship('Stipend', back_populates='organization')

    def __repr__(self):
        return f"Organization('{self.name}')"
