from app.models.stipend import Stipend
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app.extensions import db  # Importing db from extensions
import logging

def get_all_stipends():
    try:
        stipends = Stipend.query.all()
        logging.info(f"Retrieved {len(stipends)} stipends.")
        return stipends
    except SQLAlchemyError as e:
        logging.error(str(e))
        return []

def delete_stipend(stipend, session):
    try:
        session.delete(stipend)
        session.commit()
        logging.info("Stipend deleted successfully.")
    except SQLAlchemyError as e:
        logging.error(f"Error deleting stipend: {e}")
        session.rollback()

def create_stipend(data, session):
    if Stipend.query.filter_by(name=data['name']).first():
        logging.warning("Stipend with this name already exists.")
        return None  # or raise an exception, depending on your preference
    
    try:
        application_deadline = data.get('application_deadline')
        if application_deadline and not isinstance(application_deadline, datetime):
            logging.error(f"Invalid application deadline type: {type(application_deadline)}")
            return None
    except Exception as e:
        logging.error(f"Error processing application deadline: {e}")
        return None
    
    new_stipend = Stipend(**data)
    session.add(new_stipend)
    
    try:
        session.commit()
        logging.info("Stipend added to the database successfully.")
        return new_stipend
    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        session.rollback()
        return None

def get_stipend_by_id(stipend_id):
    try:
        stipend = Stipend.query.get(stipend_id)
        if stipend:
            logging.info(f"Stipend found with ID {stipend_id}: {stipend.name}")
        else:
            logging.warning(f"No stipend found with ID {stipend_id}.")
        return stipend
    except SQLAlchemyError as e:
        logging.error(str(e))
        return None

def update_stipend(stipend, data):
    stipend.name = data['name']
    stipend.summary = data.get('summary', stipend.summary)
    stipend.description = data.get('description', stipend.description)
    stipend.homepage_url = data.get('homepage_url', stipend.homepage_url)
    stipend.application_procedure = data.get('application_procedure', stipend.application_procedure)
    stipend.eligibility_criteria = data.get('eligibility_criteria', stipend.eligibility_criteria)
    
    try:
        application_deadline = data.get('application_deadline')
        if application_deadline and not isinstance(application_deadline, datetime):
            logging.error(f"Invalid application deadline type: {type(application_deadline)}")
            return None
    except Exception as e:
        logging.error(f"Error processing application deadline: {e}")
        return None
    
    stipend.open_for_applications = data.get('open_for_applications', stipend.open_for_applications)
    
    try:
        db.session.commit()
        logging.info("Stipend updated successfully.")
        return True
    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        db.session.rollback()
        return False
