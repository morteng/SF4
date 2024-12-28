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
    def create(data, user_id=None):
        """Create a new stipend with validation and audit logging"""
        from app.models.audit_log import AuditLog
        from flask import request, current_app
        from datetime import datetime
        
        # Validate application deadline
        if 'application_deadline' in data:
            # First validate date format
            if isinstance(data['application_deadline'], str):
                try:
                    data['application_deadline'] = datetime.strptime(
                        data['application_deadline'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    raise ValueError("Invalid date format. Use YYYY-MM-DD HH:MM:SS")
        
            # Then validate date range
            now = datetime.utcnow()
            if data['application_deadline'] < now:
                raise ValueError("Application deadline must be a future date")
            if (data['application_deadline'] - now).days > 365 * 5:
                raise ValueError("Application deadline cannot be more than 5 years in the future")
        
        # Validate organization exists
        if 'organization_id' in data:
            org = Organization.query.get(data['organization_id'])
            if not org:
                raise ValueError("Invalid organization ID")
        
        # Create stipend
        stipend = Stipend(**data)
        db.session.add(stipend)
        db.session.commit()
        
        # Create audit log
        try:
            AuditLog.create(
                user_id=user_id if user_id else 0,
                action='create_stipend',
                object_type='Stipend',
                object_id=stipend.id,
                details_before=None,
                details_after=stipend.to_dict(),
                ip_address=request.remote_addr if request else '127.0.0.1',
                http_method='POST',
                endpoint='admin.stipend.create'
            )
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating audit log: {str(e)}")
            raise
        
        return stipend

    def update(self, data, user_id=None):
        """Update stipend fields with audit logging"""
        from app.models.audit_log import AuditLog
        from flask import request
        from app.models.tag import Tag
        
        # Validate required fields
        required_fields = ['name', 'summary', 'description', 'homepage_url', 
                          'application_procedure', 'eligibility_criteria',
                          'application_deadline', 'organization_id']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Get current state before update
        before = self.to_dict()
        
        # Update fields
        for key, value in data.items():
            if key == 'tags':
                # Convert tag IDs to Tag instances if necessary
                self.tags = [
                    Tag.query.get(tag_id) if isinstance(tag_id, int) else tag_id
                    for tag_id in value
                ]
            else:
                setattr(self, key, value)
        
        # Commit changes
        db.session.commit()
        
        # Create audit log
        AuditLog.create(
            user_id=user_id if user_id is not None else 0,
            action='update_stipend',
            object_type='Stipend',
            object_id=self.id,
            details_before=before,
            details_after=self.to_dict(),
            ip_address=request.remote_addr if request else '127.0.0.1',
            http_method='POST',
            endpoint='admin.stipend.edit'
        )
        
        return self

    @staticmethod
    def delete(stipend_id):
        """Delete a stipend"""
        stipend = Stipend.query.get_or_404(stipend_id)
        db.session.delete(stipend)
        db.session.commit()

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
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'open_for_applications': self.open_for_applications,
            'organization_id': self.organization_id,
            'organization': self.organization.name if self.organization else None,
            'tags': [{'id': tag.id, 'name': tag.name} for tag in self.tags],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.open_for_applications and (
                not self.application_deadline or 
                self.application_deadline > datetime.utcnow()
            )
        }
