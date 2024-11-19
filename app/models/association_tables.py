from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

def init_association_tables(db):
    # This function can be used to initialize any additional setup if needed
    pass
