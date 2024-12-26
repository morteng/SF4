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
                        if value < datetime.now():
                            raise ValueError("Application deadline cannot be in the past.")
                    except ValueError:
                        raise ValueError("Invalid date format. Please use YYYY-MM-DD HH:MM:SS")
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
        required_fields = ['name', 'organization_id']
        for field in required_fields:
            if field not in stipend_data or not stipend_data[field]:
                raise ValueError(f"{field.replace('_', ' ').title()} is required")
        
        # Validate organization exists
        organization = session.get(Organization, stipend_data['organization_id'])
        if not organization:
            raise ValueError("Invalid organization ID")
        
        # Handle application_deadline
        if 'application_deadline' in stipend_data:
            if isinstance(stipend_data['application_deadline'], str):
                if stipend_data['application_deadline'].strip():
                    try:
                        deadline = datetime.strptime(
                            stipend_data['application_deadline'], '%Y-%m-%d %H:%M:%S'
                        )
                        if deadline < datetime.now():
                            raise ValueError("Application deadline cannot be in the past.")
                        stipend_data['application_deadline'] = deadline
                    except ValueError:
                        raise ValueError("Invalid date format. Please use YYYY-MM-DD HH:MM:SS")
                else:
                    stipend_data['application_deadline'] = None
            elif isinstance(stipend_data['application_deadline'], datetime):
                if stipend_data['application_deadline'] < datetime.now():
                    raise ValueError("Application deadline cannot be in the past.")
            elif not stipend_data['application_deadline']:
                stipend_data['application_deadline'] = None
            else:
                raise ValueError("Invalid date format")
        
        # Handle open_for_applications
        if 'open_for_applications' in stipend_data:
            if isinstance(stipend_data['open_for_applications'], str):
                stipend_data['open_for_applications'] = stipend_data['open_for_applications'].lower() in ['y', 'yes', 'true', '1']
            elif not isinstance(stipend_data['open_for_applications'], bool):
                raise ValueError("Open for Applications must be a boolean value.")
        
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
