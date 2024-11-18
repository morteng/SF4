from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    stipends = db.relationship('Stipend', secondary='stipend_tags', back_populates='tags')

    def __repr__(self):
        return f"<Tag(name={self.name})>"
