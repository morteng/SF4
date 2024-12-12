from app.models.tag import Tag
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db

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
        # Log the error and possibly handle it
        print(str(e))
        db.session.rollback()

def create_tag(data):
    new_tag = Tag(**data)
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
    tag.name = data['name']
    tag.category = data['category']
    db.session.commit()
