import logging
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
        
        # If 'open_for_applications' is not in the data, set it to False
        if 'open_for_applications' not in data:
            stipend.open_for_applications = False

        db.session.commit()
        return stipend
    except Exception as e:
        logging.error(f"Failed to update stipend: {e}")
        db.session.rollback()
        return None

def create_stipend(stipend):
    if Stipend.query.filter_by(name=stipend.name).first():
        return None  # Duplicate name detected
    try:
        # Validate and parse application_deadline
        if isinstance(stipend.application_deadline, str):
            try:
                stipend.application_deadline = datetime.strptime(
                    stipend.application_deadline, '%Y-%m-%d %H:%M:%S'
                )
            except ValueError:
                # Invalid date format; set to None
                stipend.application_deadline = None
        db.session.add(stipend)
        db.session.commit()
        return stipend
    except Exception as e:
        logging.error(f"Failed to create stipend: {e}")
        db.session.rollback()
        return None

def get_all_stipends():
    return Stipend.query.all()

def get_stipend_count():
    return Stipend.query.count()

def delete_stipend(stipend):
    db.session.delete(stipend)
    db.session.commit()

def get_stipend_by_id(stipend_id):
    return db.session.get(Stipend, stipend_id)
