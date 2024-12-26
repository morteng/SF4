import logging
from app.extensions import db
from app.models import Stipend, Organization
from datetime import datetime
from flask import flash
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_ERROR, FLASH_CATEGORY_SUCCESS

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

def update_stipend(stipend, data, session=db.session):
    try:
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
                if value:
                    if isinstance(value, str):
                        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    if value < datetime.now():
                        raise ValueError("Application deadline cannot be in the past.")
            elif key == 'open_for_applications' and value is not None:
                if isinstance(value, str):
                    value = value.lower() in ['y', 'yes', 'true', '1']
                else:
                    value = bool(value)

            if hasattr(stipend, key):
                setattr(stipend, key, value)

        session.commit()
        flash(FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        return True
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to update stipend: {e}")
        flash(str(e) if str(e) else FLASH_MESSAGES["UPDATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
        return False

def create_stipend(stipend_data, session=db.session):
    try:
        # Ensure organization_id is present
        if 'organization_id' not in stipend_data or not stipend_data['organization_id']:
            raise ValueError("Organization ID is required")
            
        # Handle application_deadline
        if 'application_deadline' in stipend_data:
            if stipend_data['application_deadline'] == '':
                stipend_data['application_deadline'] = None
            elif isinstance(stipend_data['application_deadline'], str):
                try:
                    stipend_data['application_deadline'] = datetime.strptime(
                        stipend_data['application_deadline'], '%Y-%m-%d %H:%M:%S'
                    )
                except ValueError:
                    raise ValueError("Invalid date format. Please use YYYY-MM-DD HH:MM:SS")
        
        # Fetch the organization
        organization_id = stipend_data['organization_id']
        organization = session.get(Organization, organization_id)
        if not organization:
            print(f"[DEBUG] Invalid organization ID: {organization_id}")
            raise ValueError(f"Invalid organization ID: {organization_id}")
        
        # Remove organization_id from stipend_data to avoid conflicts
        stipend_data.pop('organization_id', None)
        
        # Create a new Stipend object from the provided data
        print("[DEBUG] Creating Stipend object")
        new_stipend = Stipend(**stipend_data)
        
        # Explicitly set the organization relationship
        new_stipend.organization = organization
        
        # Add the new stipend to the session and commit
        session.add(new_stipend)
        session.commit()
        print("[DEBUG] Stipend created and committed successfully")
        return new_stipend
    except Exception as e:
        print(f"[DEBUG] Exception occurred: {str(e)}")
        session.rollback()
        logging.error(f"Failed to create stipend: {e}")
        raise

def delete_stipend(stipend_id):
    try:
        stipend = get_stipend_by_id(stipend_id)
        if stipend:
            db.session.delete(stipend)
            db.session.commit()
            logging.info('Stipend deleted successfully.')
            flash(FLASH_MESSAGES["DELETE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        else:
            logging.error('Stipend not found!')
            flash(FLASH_MESSAGES["STIPEND_NOT_FOUND"], FLASH_CATEGORY_ERROR)
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to delete stipend: {e}")
        flash(FLASH_MESSAGES["DELETE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)

def get_stipend_by_id(id):
    return db.session.get(Stipend, id)

def get_all_stipends():
    # Change from returning a list to returning a query object
    return Stipend.query
