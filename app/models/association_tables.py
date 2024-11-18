from sqlalchemy import Table, Column, ForeignKey, Integer

# Define the association tables without immediate db reference
stipend_tags = None
stipend_organizations = None

def init_association_tables(db):
    global stipend_tags, stipend_organizations
    stipend_tags = Table(
        'stipend_tags',
        db.metadata,
        Column('stipend_id', Integer, ForeignKey('stipends.id'), primary_key=True),
        Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
    )

    stipend_organizations = Table(
        'stipend_organizations',
        db.metadata,
        Column('stipend_id', Integer, ForeignKey('stipends.id'), primary_key=True),
        Column('organization_id', Integer, ForeignKey('organizations.id'), primary_key=True)
    )
