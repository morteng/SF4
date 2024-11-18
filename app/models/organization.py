from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    homepage_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    stipends = db.relationship('Stipend', secondary='stipend_organizations', back_populates='organizations')

    def __repr__(self):
        return f"<Organization(name={self.name})>"
