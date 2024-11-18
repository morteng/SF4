from app.models.user import User

def get_user_by_id(user_id):
    from app.extensions import db
    return db.session.get(User, user_id)

def update_user(user_id, username, email, is_admin):
    from app.extensions import db
    user = get_user_by_id(user_id)
    if user:
        user.username = username
        user.email = email
        user.is_admin = is_admin
        db.session.commit()
        return True
    return False
