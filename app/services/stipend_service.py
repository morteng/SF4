from app.models import Stipend
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db

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
