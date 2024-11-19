from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_association_tables(db):
    # Define your association tables here
    stipend_tag_association = db.Table(
        'stipend_tag',
        db.Column('stipend_id', db.Integer, db.ForeignKey('stipend.id'), primary_key=True),
        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
    )

    organization_stipends = db.Table(
        'organization_stipends',
        db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True),
        db.Column('stipend_id', db.Integer, db.ForeignKey('stipend.id'), primary_key=True)
    )

    # Add other association tables as needed

    return stipend_tag_association, organization_stipends
