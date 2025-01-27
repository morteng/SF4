from app.models.base import Base
from app.models import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Stipend(Base):
    __tablename__ = 'stipend'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    summary = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    homepage_url = db.Column(db.String(255), nullable=True)
    application_procedure = db.Column(db.Text, nullable=True)
    eligibility_criteria = db.Column(db.Text, nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=True)
    open_for_applications = db.Column(db.Boolean, default=True, nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    organization = db.relationship('Organization', backref=db.backref('stipends', lazy=True))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                           onupdate=db.func.current_timestamp(), nullable=False)
    
    def update(self, data, user_id=None):
        """Update stipend fields"""
        try:
            # Handle tags separately
            if 'tags' in data:
                tags = data.pop('tags')
                from app.models.tag import Tag
                self.tags = [Tag.query.get(tag_id) for tag_id in tags]
            
            # Update other fields
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating stipend {self.id}: {str(e)}")
            raise

    def __init__(self, **kwargs):
        # Initialize tags properly
        tags = kwargs.pop('tags', [])
        # Filter out non-model fields
        model_fields = {k: v for k, v in kwargs.items() if hasattr(self, k)}
        super().__init__(**model_fields)
        
        if tags:
            from app.models.tag import Tag
            self.tags = [Tag.query.get(tag_id) if isinstance(tag_id, int) else tag_id 
                        for tag_id in tags]

    def __repr__(self):
        return f'<Stipend {self.name}>'

    def validate(self):
        """Validate stipend data - only name is required"""
        errors = {}
        
        if not self.name:
            errors['name'] = 'Name is required'
            
        # Validate organization exists if provided
        if self.organization_id:
            from app.models.organization import Organization
            if not Organization.query.get(self.organization_id):
                errors['organization_id'] = 'Invalid organization'
                
        return errors

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
                self.application_deadline.replace(tzinfo=datetime.utcnow().tzinfo) > datetime.now(datetime.utcnow().tzinfo)
            )
        }

    # Relationships
    tags = db.relationship(
        'Tag',
        secondary=stipend_tag_association,
        back_populates='stipends',  # Changed to match Tag model
        lazy='dynamic'
    )

    organizations = db.relationship(
        'Organization', 
        secondary=organization_stipends, 
        back_populates='stipends'
    )
