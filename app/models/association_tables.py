from app.extensions import db

stipend_tags = db.Table(
    'stipend_tags',
    db.Column('stipend_id', db.Integer, db.ForeignKey('stipends.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

stipend_organizations = db.Table(
    'stipend_organizations',
    db.Column('stipend_id', db.Integer, db.ForeignKey('stipends.id'), primary_key=True),
    db.Column('organization_id', db.Integer, db.ForeignKey('organizations.id'), primary_key=True)
)
