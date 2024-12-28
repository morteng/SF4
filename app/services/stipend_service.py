import logging
from app.extensions import db
from app.models import Stipend, Organization
from datetime import datetime
from flask import flash
from app.constants import FlashMessages, FlashCategory

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

def update_stipend(stipend, data, session=db.session):
    try:
        # Ensure open_for_applications is present with default False
        if 'open_for_applications' not in data:
            data['open_for_applications'] = False

        # Handle organization_id separately
        organization_id = data.pop('organization_id', None)
        if organization_id:
            organization = session.get(Organization, organization_id)
            if not organization:
                raise ValueError(f"Invalid organization ID: {organization_id}")
            stipend.organization = organization

        # Process other fields
        for key, value in data.items():
            if key.startswith('_'):
                continue

            if key == 'application_deadline':
                if value == '':
                    value = None
                elif isinstance(value, str):
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        now = datetime.now()
                        if value < now:
                            raise ValueError("Application deadline cannot be in the past.")
                        if (value - now).days > 365 * 5:
                            raise ValueError("Application deadline cannot be more than 5 years in the future.")
                    except ValueError as e:
                        if 'does not match format' in str(e):
                            raise ValueError("Invalid date format. Please use YYYY-MM-DD HH:MM:SS")
                        elif 'day is out of range' in str(e):
                            raise ValueError("Invalid date values (e.g., Feb 30)")
                        elif 'hour must be in' in str(e):
                            raise ValueError("Invalid time values (e.g., 25:61:61)")
                        elif 'month must be in' in str(e):
                            raise ValueError("Invalid date values (e.g., Feb 30)")
                        elif 'minute must be in' in str(e):
                            raise ValueError("Invalid time values (e.g., 25:61:61)")
                        elif 'second must be in' in str(e):
                            raise ValueError("Invalid time values (e.g., 25:61:61)")
                        else:
                            raise ValueError("Invalid date/time values")
                elif isinstance(value, datetime):
                    if value < datetime.now():
                        raise ValueError("Application deadline cannot be in the past.")
                elif value is not None:
                    raise ValueError("Invalid date format")
            elif key == 'open_for_applications' and value is not None:
                if isinstance(value, str):
                    if value.lower() not in ['y', 'yes', 'true', '1', 'n', 'no', 'false', '0']:
                        raise ValueError("Open for Applications must be a boolean value.")
                    value = value.lower() in ['y', 'yes', 'true', '1']
                elif not isinstance(value, bool):
                    raise ValueError("Open for Applications must be a boolean value.")

            if hasattr(stipend, key):
                setattr(stipend, key, value)

        session.commit()
        flash(FlashMessages.UPDATE_STIPEND_SUCCESS.value, FlashCategory.SUCCESS.value)
        return True
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to create stipend: {e}")  # Add this line
        logging.error(f"Failed to update stipend: {e}")
        flash(str(e) if str(e) else FlashMessages.UPDATE_STIPEND_ERROR.value, FlashCategory.ERROR.value)
        return False

def create_stipend(stipend_data, session=db.session):
    try:
        # Validate required fields
        required_fields = ['name', 'summary', 'description', 'organization_id']
        for field in required_fields:
            if not stipend_data.get(field):
                raise ValueError(f"{field.replace('_', ' ').title()} is required")
        
        # Validate organization
        organization = session.get(Organization, stipend_data['organization_id'])
        if not organization:
            raise ValueError("Invalid organization ID")
        
        # Validate tags
        tags = []
        if 'tags' in stipend_data:
            tag_ids = stipend_data.pop('tags')
            tags = session.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            if len(tags) != len(tag_ids):
                raise ValueError("One or more invalid tags provided")
        
        # Validate application deadline
        if 'application_deadline' in stipend_data:
            deadline = stipend_data['application_deadline']
            if deadline and isinstance(deadline, str):
                try:
                    deadline = datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S')
                    if deadline < datetime.utcnow():
                        raise ValueError("Application deadline cannot be in the past")
                    stipend_data['application_deadline'] = deadline
                except ValueError as e:
                    raise ValueError("Invalid application deadline format. Use YYYY-MM-DD HH:MM:SS")
        
        # Create the stipend
        new_stipend = Stipend(**stipend_data)
        new_stipend.tags = tags
        
        session.add(new_stipend)
        session.commit()
        
        # Add audit log
        audit_log = AuditLog(
            user_id=current_user.id,
            action='create_stipend',
            details=f"Created stipend: {new_stipend.name}",
            timestamp=datetime.utcnow()
        )
        session.add(audit_log)
        session.commit()
        
        return new_stipend
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to create stipend: {e}")
        raise

def update_stipend(stipend_id, data, session=db.session):
    try:
        stipend = session.get(Stipend, stipend_id)
        if not stipend:
            raise ValueError("Stipend not found")
            
        # Handle tags
        tags = data.pop('tags', [])
        
        # Update fields
        for key, value in data.items():
            if hasattr(stipend, key):
                setattr(stipend, key, value)
                
        # Update tags
        if tags:
            stipend.tags = tags
            
        session.commit()
        return stipend
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to update stipend: {e}")
        raise

def delete_stipend(stipend_id, session=db.session):
    try:
        stipend = session.get(Stipend, stipend_id)
        if not stipend:
            raise ValueError("Stipend not found")
            
        session.delete(stipend)
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to delete stipend: {e}")
        raise

def delete_stipend(stipend_id, session=db.session):
    try:
        stipend = get_stipend_by_id(stipend_id)
        if stipend:
            session.delete(stipend)
            session.commit()
            logging.info('Stipend deleted successfully.')
            flash(FlashMessages.DELETE_STIPEND_SUCCESS.value, FlashCategory.SUCCESS.value)
        else:
            logging.error('Stipend not found!')
            flash(FlashMessages.STIPEND_NOT_FOUND.value, FlashCategory.ERROR.value)
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to delete stipend: {e}")
        flash(FlashMessages.DELETE_STIPEND_ERROR.value, FlashCategory.ERROR.value)

def get_stipend_by_id(id, session=db.session):
    return session.get(Stipend, id)

def get_all_stipends():
    return Stipend.query.all()  # Return a list instead of Query object
from app.models.stipend import Stipend
from app.models.audit_log import AuditLog
from app.extensions import db

def create_stipend(data, user_id, ip_address):
    stipend = Stipend(**data)
    db.session.add(stipend)
    db.session.commit()
    
    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action_type='create',
        object_type='stipend',
        object_id=stipend.id,
        ip_address=ip_address,
        http_method='POST',
        endpoint='/admin/stipends/create'
    )
    db.session.add(audit)
    db.session.commit()
    
    return stipend

def update_stipend(stipend_id, data, user_id, ip_address):
    stipend = Stipend.query.get_or_404(stipend_id)
    before_state = str(stipend.__dict__)
    
    for key, value in data.items():
        setattr(stipend, key, value)
    
    db.session.commit()
    
    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action_type='update',
        object_type='stipend',
        object_id=stipend.id,
        ip_address=ip_address,
        http_method='POST',
        endpoint=f'/admin/stipends/{stipend_id}/edit',
        before_state=before_state,
        after_state=str(stipend.__dict__)
    )
    db.session.add(audit)
    db.session.commit()
    
    return stipend

def delete_stipend(stipend_id, user_id, ip_address):
    stipend = Stipend.query.get_or_404(stipend_id)
    before_state = str(stipend.__dict__)
    
    db.session.delete(stipend)
    db.session.commit()
    
    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action_type='delete',
        object_type='stipend',
        object_id=stipend_id,
        ip_address=ip_address,
        http_method='POST',
        endpoint=f'/admin/stipends/{stipend_id}/delete',
        before_state=before_state
    )
    db.session.add(audit)
    db.session.commit()
