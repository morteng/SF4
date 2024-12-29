from .association_tables import stipend_tag_association, organization_stipends
from app.extensions import db
from .organization import Organization
from datetime import datetime, timezone
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

def parse_flexible_date(date_str):
    """Parse flexible date formats into datetime objects"""
    if not date_str:
        return None
    
    try:
        # Try parsing as full datetime first
        dt = parse(date_str)
        
        # Handle vague descriptions like "in August"
        if 'in ' in date_str.lower():
            month = date_str.lower().split('in ')[1].strip()
            dt = parse(month)
            # Set to end of month if only month is specified
            dt = dt + relativedelta(day=31)
            
        # Handle month/year format
        elif len(date_str.split()) == 2 and not date_str[-1].isdigit():
            dt = parse(date_str)
            dt = dt + relativedelta(day=31)
            
        # Handle year only
        elif len(date_str) == 4 and date_str.isdigit():
            dt = parse(date_str)
            dt = dt + relativedelta(month=12, day=31)
            
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None

class Stipend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    homepage_url = db.Column(db.String(255), nullable=True)
    application_procedure = db.Column(db.Text, nullable=True)
    eligibility_criteria = db.Column(db.Text, nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=True)
    open_for_applications = db.Column(db.Boolean, default=True, nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    organization = db.relationship('Organization', backref=db.backref('stipends', lazy=True))
    tags = db.relationship('Tag', secondary=stipend_tag_association, backref='stipends')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    __mapper_args__ = {"confirm_deleted_rows": False}

    @staticmethod
    def create(data, user_id=None):
        """Create a new stipend with validation and audit logging"""
        from app.services.stipend_service import StipendService
        service = StipendService()
        return service.create(data, user_id)

    def update(self, data, user_id=None):
        """Update stipend fields with audit logging and validation"""
        from app.services.stipend_service import StipendService
        service = StipendService()
        return service.update(self.id, data, user_id=user_id)

    @staticmethod
    def delete(stipend_id, user_id=None):
        """Delete a stipend with audit logging"""
        from app.services.stipend_service import StipendService
        service = StipendService()
        return service.delete(stipend_id, user_id=user_id)

    def __init__(self, **kwargs):
        # Filter out non-model fields
        model_fields = {k: v for k, v in kwargs.items() if hasattr(self, k)}
        super().__init__(**model_fields)
        
        # Handle tags separately since they need to be Tag instances
        if 'tags' in kwargs:
            from app.models.tag import Tag
            self.tags = [Tag.query.get(tag_id) if isinstance(tag_id, int) else tag_id 
                        for tag_id in kwargs['tags']]

    def __repr__(self):
        return f'<Stipend {self.name}>'

    def to_dict(self):
        """Convert stipend to dictionary with all relevant data."""
        return {
            'id': self.id,
            'name': self.name,
            'summary': self.summary,
            'description': self.description,
            'homepage_url': self.homepage_url,
            'application_procedure': self.application_procedure,
            'eligibility_criteria': self.eligibility_criteria,
            'application_deadline': (
                self.application_deadline.strftime('%B %Y') 
                if self.application_deadline and self.application_deadline.hour == 23 and self.application_deadline.minute == 59
                else self.application_deadline.strftime('%Y-%m-%d %H:%M:%S') 
                if self.application_deadline 
                else None
            ),
            'open_for_applications': self.open_for_applications,
            'organization_id': self.organization_id,
            'organization': self.organization.name if self.organization else None,
            'tags': [{'id': tag.id, 'name': tag.name} for tag in self.tags],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.open_for_applications and (
                not self.application_deadline or 
                self.application_deadline.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)
            )
        }
