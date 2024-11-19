from app.models.stipend import Stipend

def get_stipend_by_id(stipend_id):
    from app import db
    return db.session.get(Stipend, stipend_id)

def delete_stipend(stipend):
    from app import db
    db.session.delete(stipend)
