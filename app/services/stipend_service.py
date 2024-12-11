import logging
from flask import flash  # Import the flash function
from app.extensions import db
from app.models import Stipend
from datetime import datetime

logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

def update_stipend(stipend, data):
    try:
        for key, value in data.items():
            if key == 'application_deadline' and isinstance(value, str):
                try:
                    value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    value = None  # Handle invalid date format
            if hasattr(stipend, key):
                setattr(stipend, key, value)
                logging.info(f"Setting {key} to {value}")  # Add this line for logging
        
        db.session.commit()
        flash('Stipend updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        if stipend not in db.session:
            db.session.add(stipend)  # Re-attach the stipend object to the session
        logging.error(f"Failed to update stipend: {e}")
        flash('Failed to update stipend. Please try again.', 'danger')

def create_stipend(stipend):
    try:
        db.session.add(stipend)
        db.session.commit()
        flash('Stipend created successfully.', 'success')
        return stipend
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to create stipend: {e}")
        flash('Failed to create stipend. Please try again.', 'danger')
        return None

def delete_stipend(stipend_id):
    try:
        stipend = get_stipend_by_id(stipend_id)
        if stipend:
            db.session.delete(stipend)
            db.session.commit()
            flash('Stipend deleted successfully.', 'success')
        else:
            flash('Stipend not found!', 'danger')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to delete stipend: {e}")
        flash('Failed to delete stipend. Please try again.', 'danger')

def get_stipend_by_id(id):
    return db.session.get(Stipend, id)

def get_all_stipends():
    return Stipend.query.all()
