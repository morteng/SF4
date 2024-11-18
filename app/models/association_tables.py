from sqlalchemy import Table, Column, ForeignKey, Integer
from app.models import db

# Association table for many-to-many relationship between Stipend and Tag
stipend_tags = Table(
    'stipend_tags',
    db.Model.metadata,
    Column('stipend_id', Integer, ForeignKey('stipends.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

# Association table for many-to-many relationship between Stipend and Organization
stipend_organizations = Table(
    'stipend_organizations',
    db.Model.metadata,
    Column('stipend_id', Integer, ForeignKey('stipends.id'), primary_key=True),
    Column('organization_id', Integer, ForeignKey('organizations.id'), primary_key=True)
)
