from app.models.user import User

def get_user_by_id(user_id):
    from app import db
    return db.session.get(User, user_id)

def delete_user(user):
    from app import db
    db.session.delete(user)
