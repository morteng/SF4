import logging
from app.models.stipend import Stipend
from app.extensions import db

def create_stipend(stipend):
    if Stipend.query.filter_by(name=stipend.name).first():
        return None  # Duplicate name detected
    try:
        db.session.add(stipend)
        db.session.commit()
        return stipend
    except Exception as e:
        logging.error(f"Failed to create stipend: {e}")
        db.session.rollback()
        return None

def update_stipend(stipend):
    try:
        db.session.commit()
        db.session.refresh(stipend)
    except Exception as e:
        logging.error(f"Failed to update stipend: {e}")
        db.session.rollback()

def get_all_stipends():
    return Stipend.query.all()

def get_stipend_count():
    return Stipend.query.count()

def delete_stipend(stipend):
    db.session.delete(stipend)
    db.session.commit()

def get_stipend_by_id(stipend_id):
    return Stipend.query.get_or_404(stipend_id)
