from app import db

stipend_organizations = db.Table(
    'stipend_organizations',
    db.Column('stipend_id', db.Integer, db.ForeignKey('stipends.id'), primary_key=True),
    db.Column('organization_id', db.Integer, db.ForeignKey('organizations.id'), primary_key=True)
)
