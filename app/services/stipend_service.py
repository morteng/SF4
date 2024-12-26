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
                if value == '':
                    value = None
                elif isinstance(value, str):
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        value = None  # Set to None if invalid format
                if value and value < datetime.now():
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
        # Validate required fields
        if 'organization_id' not in stipend_data or not stipend_data['organization_id']:
            raise ValueError("Organization ID is required")
            
        # Handle application_deadline
        if 'application_deadline' in stipend_data:
            if isinstance(stipend_data['application_deadline'], str):
                try:
                    stipend_data['application_deadline'] = datetime.strptime(
                        stipend_data['application_deadline'], '%Y-%m-%d %H:%M:%S'
                    )
                except ValueError:
                    raise ValueError("Invalid date format. Please use YYYY-MM-DD HH:MM:SS")
            elif isinstance(stipend_data['application_deadline'], datetime):
                pass  # Already a datetime object
            else:
                stipend_data['application_deadline'] = None  # Set to None if invalid
        
        # Create the stipend
        new_stipend = Stipend(**stipend_data)
        session.add(new_stipend)
        session.commit()
        return new_stipend
    except Exception as e:
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
    return Stipend.query.all()  # Return a list instead of Query object
