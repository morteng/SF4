from sqlalchemy import Table, Integer, ForeignKey, Column
from app.models.base_model import BaseModel

stipend_tag_association = Table(
    'stipend_tag_association',
    BaseModel.metadata,
    Column('stipend_id', Integer, ForeignKey('stipends.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)
