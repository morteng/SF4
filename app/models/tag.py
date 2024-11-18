from app.extensions import db
from .association_tables import stipend_tags

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)

    # Relationships
    stipends = db.relationship('Stipend', secondary=stipend_tags, back_populates='tags')
