from app.models.tag import Tag
from app.extensions import db

def get_all_tags():
    return Tag.query.all()

def get_tag_by_id(tag_id):
    return Tag.query.get(tag_id)

def create_tag(name, category):
    tag = Tag(name=name, category=category)
    db.session.add(tag)
    db.session.commit()
    return tag

def update_tag(tag_id, name=None, category=None):
    tag = get_tag_by_id(tag_id)
    if not tag:
        raise ValueError("Tag not found")
    
    if name is not None:
        tag.name = name
    if category is not None:
        tag.category = category
    
    db.session.commit()
    return tag

def delete_tag(tag_id):
    tag = get_tag_by_id(tag_id)
    if not tag:
        raise ValueError("Tag not found")
    
    db.session.delete(tag)
    db.session.commit()
