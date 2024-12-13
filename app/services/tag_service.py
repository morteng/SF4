from app.models.tag import Tag
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from wtforms.validators import ValidationError

def get_all_tags():
    try:
        return Tag.query.all()
    except SQLAlchemyError as e:
        # Log the error
        print(str(e))
        return []

def delete_tag(tag):
    try:
        db.session.delete(tag)
        db.session.commit()
    except SQLAlchemyError as e:
        # Log the error and re-raise it
        print(str(e))
        db.session.rollback()
        raise  # Re-raise the exception

def create_tag(data):
    new_tag = Tag(name=data['name'], category=data['category'])
    db.session.add(new_tag)
    db.session.commit()
    return new_tag

def get_tag_by_id(tag_id):
    try:
        return db.session.get(Tag, tag_id)  # Corrected line
    except SQLAlchemyError as e:
        # Log the error
        print(str(e))
        return None

def update_tag(tag, data):
    if not data['name']:
        raise ValidationError('Name cannot be empty.')
    if not data['category']:
        raise ValidationError('Category cannot be empty.')

    tag.name = data['name']
    tag.category = data['category']
    db.session.commit()
