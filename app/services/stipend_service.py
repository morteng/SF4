from app.models.stipend import Stipend
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
import logging

logging.basicConfig(level=logging.ERROR)

def get_all_stipends():
    try:
        return Stipend.query.all()
    except SQLAlchemyError as e:
        logging.error(str(e))
        return []

def delete_stipend(stipend):
    try:
        db.session.delete(stipend)
        db.session.commit()
    except SQLAlchemyError as e:
        logging.error(str(e))
        db.session.rollback()

def create_stipend(data):
    new_stipend = Stipend(**data)
    db.session.add(new_stipend)
    db.session.commit()
    return new_stipend

def get_stipend_by_id(stipend_id):
    try:
        return Stipend.query.get(stipend_id)
    except SQLAlchemyError as e:
        logging.error(str(e))
        return None

def update_stipend(stipend, data):
    for key, value in data.items():
        setattr(stipend, key, value)
    db.session.commit()
