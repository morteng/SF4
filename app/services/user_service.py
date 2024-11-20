from app.models.user import User

def get_user_by_id(user_id):
    return User.query.get(user_id)

def delete_user(user):
    from app.extensions import db
    db.session.delete(user)
    db.session.commit()

def get_all_users():
    return User.query.all()
