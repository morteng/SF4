from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Stipend(db.Model):
    __tablename__ = 'stipends'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    homepage_url = db.Column(db.String(255), nullable=False)
    application_procedure = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.Text, nullable=False)
    application_deadline = db.Column(db.DateTime, nullable=False)
    open_for_applications = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    tags = db.relationship('Tag', secondary='stipend_tags', back_populates='stipends')
    organizations = db.relationship('Organization', secondary='stipend_organizations', back_populates='stipends')

    def __repr__(self):
        return f"<Stipend(name={self.name})>"
