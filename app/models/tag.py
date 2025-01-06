from app.extensions import db
from .association_tables import stipend_tag_association

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    category = db.Column(db.String(100), nullable=False)  # Add this if missing
    description = db.Column(db.Text)

    # Ensure the relationship is defined
    stipends = db.relationship('Stipend', secondary=stipend_tag_association, back_populates='tags')

    __mapper_args__ = {"confirm_deleted_rows": False}

    def __repr__(self):
        return f'<Tag {self.name}>'
