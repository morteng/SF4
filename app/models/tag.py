from app.extensions import db
from .association_tables import stipend_tag_association

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    category = db.Column(db.String(100), nullable=False)  # Add this if missing
    description = db.Column(db.Text)

    # Define relationship with Stipend through association table
    stipends = db.relationship(
        'Stipend',
        secondary=stipend_tag_association,
        back_populates='tags',  # Changed to back_populates to match Stipend model
        lazy='dynamic'
    )

    __mapper_args__ = {"confirm_deleted_rows": False}

    def __repr__(self):
        return f'<Tag {self.name}>'
