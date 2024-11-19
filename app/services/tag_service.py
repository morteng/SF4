from app.models.tag import Tag

def get_tag_by_id(tag_id):
    from app import db
    return db.session.get(Tag, tag_id)

def delete_tag(tag):
    from app import db
    db.session.delete(tag)
