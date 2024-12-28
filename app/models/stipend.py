from .association_tables import stipend_tag_association, organization_stipends
from app.extensions import db
from .organization import Organization
from datetime import datetime

class Stipend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    homepage_url = db.Column(db.String(255), nullable=False)
    application_procedure = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.Text, nullable=False)
    application_deadline = db.Column(db.DateTime, nullable=False)
    open_for_applications = db.Column(db.Boolean, default=True, nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship('Organization', backref=db.backref('stipends', lazy=True))
    tags = db.relationship('Tag', secondary=stipend_tag_association, backref='stipends')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    __mapper_args__ = {"confirm_deleted_rows": False}

    @staticmethod
    def create(data):
        """Create a new stipend with validation"""
        stipend = Stipend(**data)
        db.session.add(stipend)
        db.session.commit()
        return stipend

    def update(self, data):
        """Update stipend fields"""
        for key, value in data.items():
            setattr(self, key, value)
        db.session.commit()
        return self

    @staticmethod
    def delete(stipend_id):
        """Delete a stipend"""
        stipend = Stipend.query.get_or_404(stipend_id)
        db.session.delete(stipend)
        db.session.commit()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'tags' in kwargs:
            self.tags = kwargs['tags']

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
            'organization_id': self.organization_id,
            'tags': [tag.name for tag in self.tags],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
