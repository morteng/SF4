from app.models.stipend import Stipend
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from datetime import datetime

def get_all_stipends():
    try:
        return Stipend.query.all()
    except SQLAlchemyError as e:
        # Log the error
        print(str(e))
        return []

def delete_stipend(stipend):
    try:
        db.session.delete(stipend)
        db.session.commit()
    except SQLAlchemyError as e:
        # Log the error and possibly handle it more gracefully
        print(f"Error deleting stipend: {e}")
        db.session.rollback()

def create_stipend(data):
    if Stipend.query.filter_by(name=data['name']).first():
        print("Stipend with this name already exists.")
        return None  # or raise an exception, depending on your preference
    
    try:
        application_deadline = data.get('application_deadline')
        if application_deadline and isinstance(application_deadline, datetime):
            pass
        else:
            data['application_deadline'] = None
    except ValueError as e:
        print(f"Invalid application deadline: {e}")  # Debugging statement
        data['application_deadline'] = None
    
    new_stipend = Stipend(**data)
    db.session.add(new_stipend)
    
    try:
        db.session.commit()
        print("Stipend added to the database successfully.")  # Debugging statement
        return new_stipend
    except SQLAlchemyError as e:
        print(f"Database error: {e}")  # Debugging statement
        db.session.rollback()
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
        if application_deadline and isinstance(application_deadline, datetime):
            pass
        else:
            stipend.application_deadline = None
    except ValueError as e:
        print(str(e))
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

def get_stipend_count():
    return Stipend.query.count()
