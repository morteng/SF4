from app.models.tag import Tag

def get_tag_by_id(tag_id):
    return Tag.query.get(tag_id)

def delete_tag(tag):
    from app.extensions import db
    db.session.delete(tag)
    db.session.commit()

def get_all_tags():
    from app.models.tag import Tag
    return Tag.query.all()
