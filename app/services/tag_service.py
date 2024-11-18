from app.models.tag import Tag

def get_tag_by_id(tag_id):
    from app.extensions import db
    return db.session.get(Tag, tag_id)

def update_tag(tag_id, name, category):
    from app.extensions import db
    tag = get_tag_by_id(tag_id)
    if tag:
        tag.name = name
        tag.category = category
        db.session.commit()
        return True
    return False
