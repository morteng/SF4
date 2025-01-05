from .association_tables import stipend_tag_association, organization_stipends
from . import db

class Stipend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    summary = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    homepage_url = db.Column(db.String(255), nullable=False)
    application_procedure = db.Column(db.Text, nullable=True)
    eligibility_criteria = db.Column(db.Text, nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=True)
    open_for_applications = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)

    def __repr__(self):
        return f'<Stipend {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'summary': self.summary,
            'description': self.description,
            'homepage_url': self.homepage_url,
            'application_procedure': self.application_procedure,
            'eligibility_criteria': self.eligibility_criteria,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'open_for_applications': self.open_for_applications,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    # Relationships
    tags = db.relationship('Tag', secondary=stipend_tag_association, back_populates='stipends')
    organizations = db.relationship('Organization', secondary=organization_stipends, back_populates='stipends')
