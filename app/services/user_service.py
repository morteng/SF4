from app.models.user import User
from app.extensions import db

def get_user_by_id(user_id):
    return User.query.get(user_id)

def delete_user(user):
    db.session.delete(user)
    db.session.commit()

def get_all_users():
    from app.models.user import User
    return User.query.all()

def update_user(user):
    db.session.commit()
