from app.models.stipend import Stipend
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app.extensions import db  # Importing db from extensions

def get_all_stipends():
    try:
        return Stipend.query.all()
    except SQLAlchemyError as e:
        # Log the error
        print(str(e))
        return []

def delete_stipend(stipend, session):
    try:
        session.delete(stipend)
        session.commit()
    except SQLAlchemyError as e:
        # Log the error and possibly handle it more gracefully
        print(f"Error deleting stipend: {e}")
        session.rollback()

def create_stipend(data, session):
    if Stipend.query.filter_by(name=data['name']).first():
        print("Stipend with this name already exists.")
        return None  # or raise an exception, depending on your preference
    
    try:
        application_deadline = data.get('application_deadline')
        if application_deadline and not isinstance(application_deadline, datetime):
            print(f"Invalid application deadline type: {type(application_deadline)}")
            return None
    except Exception as e:
        print(f"Error processing application deadline: {e}")
        return None
    
    new_stipend = Stipend(**data)
    session.add(new_stipend)
    
    try:
        session.commit()
        print("Stipend added to the database successfully.")  # Debugging statement
        return new_stipend
    except SQLAlchemyError as e:
        print(f"Database error: {e}")  # Debugging statement
        session.rollback()
        return None

def get_stipend_by_id(stipend_id):
    try:
        return Stipend.query.get(stipend_id)
    except SQLAlchemyError as e:
        # Log the error
        print(str(e))
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
            print(f"Invalid application deadline type: {type(application_deadline)}")
            return None
    except Exception as e:
        print(f"Error processing application deadline: {e}")
        return None
    
    stipend.open_for_applications = data.get('open_for_applications', stipend.open_for_applications)
    
    try:
        db.session.commit()
        print("Stipend updated successfully.")  # Debugging statement
        return True
    except SQLAlchemyError as e:
        print(f"Database error: {e}")  # Debugging statement
        db.session.rollback()
        return False
