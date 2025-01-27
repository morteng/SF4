from sqlalchemy import Table, Integer, ForeignKey
from app.models.base import Base

stipend_tag_association = Table(
    'stipend_tag_association',
    Base.metadata,
    Column('stipend_id', Integer, ForeignKey('stipend.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)
