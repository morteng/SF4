from app.models.tag import Tag
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from flask import flash  # Import flash to display messages

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
        # Log the error and flash a message
        print(str(e))
        flash(f"Failed to update tag: {str(e)}.", 'danger')
        db.session.rollback()
        raise  # Re-raise the exception if needed for further handling
