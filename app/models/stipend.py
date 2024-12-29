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
        from app.models.audit_log import AuditLog
        from flask import request, current_app
        from datetime import datetime
        
        # Validate required field
        if 'name' not in data or not data['name']:
            raise ValueError("Name is required")
        
        # Validate application deadline if provided
        if 'application_deadline' in data and data['application_deadline'] and (isinstance(data['application_deadline'], str) and data['application_deadline'].strip()):
            parsed_dt = parse_flexible_date(data['application_deadline'])
            if not parsed_dt:
                raise ValueError("Invalid date format. Use YYYY-MM-DD HH:MM:SS, Month YYYY, or YYYY")
            
            now = datetime.now(timezone.utc)
            if parsed_dt < now:
                raise ValueError("Application deadline must be a future date")
            if (parsed_dt - now).days > 365 * 5:
                raise ValueError("Application deadline cannot be more than 5 years in the future")
            
            data['application_deadline'] = parsed_dt
        
        # Validate organization exists if provided
        if 'organization_id' in data and data['organization_id']:
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
        """Update stipend fields with audit logging and validation"""
        from app.models.audit_log import AuditLog
        from flask import request, current_app
        from app.models.tag import Tag
        
        # Get current state before update
        before = self.to_dict()
        
        try:
            # Validate required fields
            if 'name' not in data:
                raise ValueError("Name is required")
            if 'summary' not in data:
                raise ValueError("Summary is required")
            if 'description' not in data:
                raise ValueError("Description is required")
            
            # Validate required fields if they're being updated
            if 'name' in data and not data['name']:
                raise ValueError("Name is required")
            if 'summary' in data and not data['summary']:
                raise ValueError("Summary is required")
            if 'description' in data and not data['description']:
                raise ValueError("Description is required")
            
            # Update fields if they exist in data
            if 'name' in data:
                self.name = data['name']
            if 'summary' in data:
                self.summary = data['summary']
            if 'description' in data:
                self.description = data['description']
            if 'homepage_url' in data:
                self.homepage_url = data['homepage_url']
            if 'application_procedure' in data:
                self.application_procedure = data['application_procedure']
            if 'eligibility_criteria' in data:
                self.eligibility_criteria = data['eligibility_criteria']
            if 'application_deadline' in data:
                parsed_dt = parse_flexible_date(data['application_deadline'])
                if not parsed_dt:
                    raise ValueError("Invalid date format. Use YYYY-MM-DD HH:MM:SS, Month YYYY, or YYYY")
                
                now = datetime.now(timezone.utc)
                if parsed_dt < now:
                    raise ValueError("Application deadline must be a future date")
                if (parsed_dt - now).days > 365 * 5:
                    raise ValueError("Application deadline cannot be more than 5 years in the future")
                
                self.application_deadline = parsed_dt
            if 'organization_id' in data:
                org = Organization.query.get(data['organization_id'])
                if not org:
                    raise ValueError("Invalid organization ID")
                self.organization_id = data['organization_id']
            if 'open_for_applications' in data:
                self.open_for_applications = data['open_for_applications']
            if 'tags' in data:
                self.tags = [
                    Tag.query.get(tag_id) if isinstance(tag_id, int) else tag_id
                    for tag_id in data['tags']
                ]
            
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
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating stipend {self.id}: {str(e)}")
            raise

    @staticmethod
    def delete(stipend_id, user_id=None):
        """Delete a stipend with audit logging"""
        from app.models.audit_log import AuditLog
        from flask import request, current_app
        
        stipend = Stipend.query.get_or_404(stipend_id)
        
        # Create audit log before deletion
        try:
            AuditLog.create(
                user_id=user_id if user_id else 0,
                action='delete_stipend',
                object_type='Stipend',
                object_id=stipend.id,
                details_before=stipend.to_dict(),
                details=f"Deleted stipend: {stipend.name} (ID: {stipend.id})",
                ip_address=request.remote_addr if request else '127.0.0.1',
                http_method='POST',
                endpoint='admin.stipend.delete'
            )
        except Exception as e:
            current_app.logger.error(f"Error creating audit log: {str(e)}")
            raise
        
        # Delete the stipend
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
