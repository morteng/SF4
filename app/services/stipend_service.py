from app.models.stipend import Stipend
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
import logging

logging.basicConfig(level=logging.ERROR)

def get_all_stipends():
    """Retrieve all stipends."""
    try:
        return Stipend.query.all()
    except SQLAlchemyError as e:
        logging.error(str(e))
        return []

def delete_stipend(stipend):
    """Delete the specified stipend."""
    try:
        db.session.delete(stipend)
        db.session.commit()
    except SQLAlchemyError as e:
        logging.error(str(e))
        db.session.rollback()

def create_stipend(data):
    """Create a new stipend."""
    try:
        new_stipend = Stipend(**data)
        db.session.add(new_stipend)
        db.session.commit()
        return new_stipend
    except SQLAlchemyError as e:
        logging.error(str(e))
        db.session.rollback()
        return None

def get_stipend_by_id(stipend_id):
    """Retrieve a stipend by its ID."""
    try:
        return Stipend.query.get(stipend_id)
    except SQLAlchemyError as e:
        logging.error(str(e))
        return None

def update_stipend(stipend, data):
    """Update the specified stipend with new data."""
    try:
        for key, value in data.items():
            setattr(stipend, key, value)
        db.session.commit()
    except SQLAlchemyError as e:
        logging.error(str(e))
        db.session.rollback()
