from app.models.organization import Organization
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func
from app.extensions import db
import logging

logger = logging.getLogger(__name__)

class OrganizationService(BaseService):
    def __init__(self, audit_logger=None):
        super().__init__(Organization, audit_logger)

    def get_all_organizations(self):
        """Get all organizations ordered by name."""
        try:
            return Organization.query.order_by(func.lower(Organization.name)).all()
        except SQLAlchemyError as e:
        logger.error(f"Error getting all organizations: {str(e)}")
        return []

def get_organization_by_id(organization_id):
    """Get organization by ID."""
    try:
        return db.session.get(Organization, organization_id)
    except SQLAlchemyError as e:
        logger.error(f"Error getting organization by ID {organization_id}: {str(e)}")
        return None

from typing import Tuple, Union
from app.utils import validate_url

def create_organization(data: dict) -> Tuple[bool, Union[Organization, str]]:
    """Create a new organization with validated data.
    
    Args:
        data: Dictionary containing organization data (name, description, homepage_url)
        
    Returns:
        Tuple of (success: bool, result: Organization or error_message: str)
    """
    # Input validation
    if not data or not isinstance(data, dict):
        return False, "Invalid organization data"
        
    name = data.get('name', '').strip()
    if not name:
        return False, "Organization name is required."
    if len(name) > 100:
        return False, "Organization name cannot exceed 100 characters."
        
    # URL validation
    homepage_url = data.get('homepage_url', '').strip()
    if homepage_url and not validate_url(homepage_url):
        return False, "Invalid homepage URL format"
        
    try:
        # Check for existing organization with same name (case-insensitive)
        existing_org = Organization.query.filter(
            func.lower(Organization.name) == func.lower(name)
        ).first()
        if existing_org:
            return False, "Organization with this name already exists."
        
        # Create new organization
        organization = Organization(
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            homepage_url=data.get('homepage_url', '').strip() or None
        )
        db.session.add(organization)
        db.session.commit()
        logger.info(f"Organization created successfully: {organization.name}")
        return True, organization
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error creating organization: {str(e)}")
        return False, "Organization with this name already exists."
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating organization: {str(e)}")
        return False, "Database error occurred while creating organization."
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error creating organization: {str(e)}")
        return False, "An unexpected error occurred."

def update_organization(organization, data):
    """Update an existing organization."""
    try:
        if not organization:
            return False, "Organization not found."
        
        # Check if name is being changed and if new name is unique
        new_name = data.get('name', '').strip()
        if new_name and new_name.lower() != organization.name.lower():
            existing_org = Organization.query.filter(
                func.lower(Organization.name) == func.lower(new_name)
            ).first()
            if existing_org:
                return False, "Organization with this name already exists."
            
            organization.name = new_name
        
        # Update other fields
        organization.description = data.get('description', organization.description).strip()
        homepage_url = data.get('homepage_url', '').strip()
        organization.homepage_url = homepage_url if homepage_url else None
        
        db.session.commit()
        logger.info(f"Organization updated successfully: {organization.name}")
        return True, organization
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error updating organization: {str(e)}")
        return False, "Organization with this name already exists."
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error updating organization: {str(e)}")
        return False, "Database error occurred while updating organization."
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error updating organization: {str(e)}")
        return False, "An unexpected error occurred."

def delete_organization(organization):
    """Delete an organization."""
    try:
        if not organization:
            return False, "Organization not found."
        
        # Check for dependent records
        if organization.stipends.count() > 0:
            return False, "Cannot delete organization with associated stipends."
        
        db.session.delete(organization)
        db.session.commit()
        logger.info(f"Organization deleted successfully: {organization.name}")
        return True, None
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error deleting organization: {str(e)}")
        return False, "Database error occurred while deleting organization."
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error deleting organization: {str(e)}")
        return False, "An unexpected error occurred."
