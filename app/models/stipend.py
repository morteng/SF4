from .association_tables import stipend_tag_association, organization_stipends
from app.extensions import db
from .organization import Organization
    
class Stipend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    homepage_url = db.Column(db.String(255), nullable=True)
    application_procedure = db.Column(db.Text, nullable=True)
    eligibility_criteria = db.Column(db.Text, nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=True)
    open_for_applications = db.Column(db.Boolean, default=True, nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    organization = db.relationship('Organization', backref=db.backref('stipends', lazy=True))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Remove the organization_id validation temporarily
        # if not self.organization_id:
        #     raise ValueError("Organization ID is required")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    __mapper_args__ = {"confirm_deleted_rows": False}

    def __repr__(self):
        return f'<Stipend {self.name}>'
