from app.models.base import Base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.models.relationships import stipend_tag_association

class Tag(Base):
    __tablename__ = 'tag'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    category = Column(String(100), nullable=False)
    description = Column(String(500))

    stipends = relationship('Stipend', secondary=stipend_tag_association, back_populates='tags')

    __mapper_args__ = {"confirm_deleted_rows": False}

    def __repr__(self):
        return f'<Tag {self.name}>'
