from app.models.tag import Tag
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
import logging

logging.basicConfig(level=logging.ERROR)

def get_all_tags():
    """Retrieve all tags."""
    try:
        return Tag.query.all()
    except SQLAlchemyError as e:
        logging.error(str(e))
        return []

def delete_tag(tag):
    """Delete the specified tag."""
    try:
        db.session.delete(tag)
        db.session.commit()
    except SQLAlchemyError as e:
        logging.error(str(e))
        db.session.rollback()

def create_tag(data):
    """Create a new tag."""
    try:
        new_tag = Tag(**data)
        db.session.add(new_tag)
        db.session.commit()
        return new_tag
    except SQLAlchemyError as e:
        logging.error(str(e))
        db.session.rollback()
        return None

def get_tag_by_id(tag_id):
    """Retrieve a tag by its ID."""
    try:
        return Tag.query.get(tag_id)
    except SQLAlchemyError as e:
        logging.error(str(e))
        return None

def update_tag(tag, data):
    """Update the specified tag with new data."""
    try:
        for key, value in data.items():
            setattr(tag, key, value)
        db.session.commit()
    except SQLAlchemyError as e:
        logging.error(str(e))
        db.session.rollback()
