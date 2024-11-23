from app.models.stipend import Stipend

def get_stipend_by_id(stipend_id):
    return Stipend.query.get(stipend_id)

def delete_stipend(stipend):
    from app.extensions import db
    db.session.delete(stipend)
    db.session.commit()

def get_all_stipends():
    from app.models.stipend import Stipend
    return Stipend.query.all()
