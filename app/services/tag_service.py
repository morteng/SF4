from app.models.tag import Tag
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
import logging  # Import logging to log errors

# Configure logging
logging.basicConfig(level=logging.ERROR)

def update_tag(tag, data):
    if not data['name']:
        raise ValidationError('Name cannot be empty.')
    if not data['category']:
        raise ValidationError('Category cannot be empty.')

    tag.name = data['name']
    tag.category = data['category']
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        # Log the error
        logging.error(f"Failed to update tag: {str(e)}.")
        db.session.rollback()
        raise  # Re-raise the exception if needed for further handling

def get_all_tags():
    return Tag.query.all()

def get_tag_by_id(tag_id):
    return db.session.get(Tag, tag_id)

def create_tag(data):
    if not data.get('name') or not data.get('category'):
        raise ValidationError('Name and category are required.')

    tag = Tag(name=data['name'], category=data['category'])
    db.session.add(tag)
    try:
        db.session.commit()
        return tag
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Failed to create tag: {str(e)}.")
        raise

def delete_tag(tag):
    db.session.delete(tag)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Failed to delete tag: {str(e)}.")
        raise
