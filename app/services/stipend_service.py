import logging
from app.extensions import db
from app.models import Stipend, Organization
from datetime import datetime
from flask import flash
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_ERROR, FLASH_CATEGORY_SUCCESS

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

def update_stipend(stipend, data, session=db.session):
    try:
        logging.info(f"Original stipend state: {stipend.__dict__}")
        
        for key, value in data.items():
            if key.startswith('_'):
                continue  # Skip internal attributes

            if key == 'application_deadline':
                if isinstance(value, str):
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        raise ValueError("Invalid date format. Please use YYYY-MM-DD HH:MM:SS.")
            elif key == 'open_for_applications' and value is not None:
                # Convert various representations of False to actual False
                if isinstance(value, str):
                    value = value.lower() in ['y', 'yes', 'true', '1']
                else:
                    value = bool(value)
            
            logging.info(f"Setting {key} to {value}")
            if hasattr(stipend, key):
                setattr(stipend, key, value)

        logging.info(f"Updated stipend state: {stipend.__dict__}")
        
        session.commit()
        flash(FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
    except Exception as e:
        session.rollback()
        if session.is_active and db.inspect(stipend).detached:
            session.add(stipend)
        logging.error(f"Failed to update stipend: {e}")
        flash(FLASH_MESSAGES["UPDATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)

def create_stipend(stipend_data, session=db.session):
    try:
        # Handle empty application deadline
        if 'application_deadline' in stipend_data and (stipend_data['application_deadline'] == '' or stipend_data['application_deadline'] is None):
            stipend_data['application_deadline'] = None
            
        # Ensure organization_id is valid
        organization_id = stipend_data.get('organization_id')
        if not organization_id:
            raise ValueError("Organization ID is required.")
        
        # Fetch the organization
        organization = session.get(Organization, organization_id)
        if not organization:
            raise ValueError("Invalid organization ID.")
        
        # Create a new Stipend object from the provided data
        new_stipend = Stipend(**stipend_data)
        
        # Convert application_deadline to datetime if it's a non-empty string
        if isinstance(new_stipend.application_deadline, str) and new_stipend.application_deadline.strip():
            try:
                new_stipend.application_deadline = datetime.strptime(new_stipend.application_deadline, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError("Invalid date format. Please use YYYY-MM-DD HH:MM:SS.")
        
        # Add the new stipend to the session and commit
        session.add(new_stipend)
        session.commit()
        logging.info('Stipend created successfully.')
        return new_stipend
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to create stipend: {e}")
        raise  # Re-raise the exception to be handled by the route

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
    # Return the query object directly without executing it
    return Stipend.query
