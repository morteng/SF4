from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

stipend_tags = db.Table(
    'stipend_tags',
    db.Column('stipend_id', db.Integer, db.ForeignKey('stipend.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

stipend_organizations = db.Table(
    'stipend_organizations',
    db.Column('stipend_id', db.Integer, db.ForeignKey('stipend.id'), primary_key=True),
    db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True)
)
