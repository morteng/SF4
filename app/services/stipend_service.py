import logging
from app.extensions import db
from app.models import Stipend
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

def create_stipend(stipend, session=db.session):
    try:
        if isinstance(stipend.application_deadline, str):
            try:
                logging.info(f"Attempting to parse application deadline: {stipend.application_deadline}")
                stipend.application_deadline = datetime.strptime(stipend.application_deadline, '%Y-%m-%d %H:%M:%S')
            except ValueError as ve:
                logging.error(f"Invalid date format: {ve}")
                flash(FLASH_MESSAGES["INVALID_DATE_FORMAT"], FLASH_CATEGORY_ERROR)
                raise ValueError("Invalid date format. Please use YYYY-MM-DD HH:MM:SS.")

        session.add(stipend)
        session.commit()
        logging.info('Stipend created successfully.')
        flash(FLASH_MESSAGES["CREATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        return stipend
    except ValueError as ve:
        session.rollback()
        logging.error(f"Failed to create stipend due to invalid input: {ve}")
        flash(FLASH_MESSAGES["CREATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
        return None
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to create stipend: {e}")
        flash(FLASH_MESSAGES["CREATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
        return None

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
    return Stipend.query.all()
