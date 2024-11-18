from app.models.user import User

def get_user_by_id(user_id):
    return User.query.get(user_id)

def list_all_users():
    return User.query.all()
