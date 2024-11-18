from sqlalchemy import Table, Column, Integer, ForeignKey
from app.extensions import db

stipend_tags = Table(
    'stipend_tags',
    db.Model.metadata,
    Column('stipend_id', Integer, ForeignKey('stipend.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True)
)

organization_stipends = Table(
    'organization_stipends',
    db.Model.metadata,
    Column('organization_id', Integer, ForeignKey('organization.id'), primary_key=True),
    Column('stipend_id', Integer, ForeignKey('stipend.id'), primary_key=True)
)
