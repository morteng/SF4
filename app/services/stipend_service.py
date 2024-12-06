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
        # Log the error and possibly handle it
        print(str(e))
        db.session.rollback()

def create_stipend(data):
    if Stipend.query.filter_by(name=data['name']).first():
        return None  # or raise an exception, depending on your preference
    try:
        data['application_deadline'] = datetime.strptime(data['application_deadline'], '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        print(str(e))
        return None
    new_stipend = Stipend(**data)
    db.session.add(new_stipend)
    db.session.commit()
    return new_stipend

def get_stipend_by_id(stipend_id):
    try:
        return Stipend.query.get(stipend_id)
    except SQLAlchemyError as e:
        # Log the error
        print(str(e))
        return None

def update_stipend(stipend, data):
    stipend.name = data['name']
    stipend.summary = data['summary']
    stipend.description = data['description']
    stipend.homepage_url = data['homepage_url']
    stipend.application_procedure = data['application_procedure']
    stipend.eligibility_criteria = data['eligibility_criteria']
    try:
        stipend.application_deadline = datetime.strptime(data['application_deadline'], '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        print(str(e))
        return None
    stipend.open_for_applications = data['open_for_applications']
    db.session.commit()
