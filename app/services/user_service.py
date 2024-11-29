from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.extensions import db

def get_user_by_id(user_id):
    return User.query.get(user_id)

def delete_user(user):
    db.session.delete(user)
    db.session.commit()

def get_all_users():
    return User.query.all()

def create_user(form_data):
    username = form_data['username']
    email = form_data['email']
    password = form_data['password']
    is_admin = form_data.get('is_admin', False)

    new_user = User(username=username, email=email, is_admin=is_admin)
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Username or email already exists")
    
    return new_user

def update_user(user):
    db.session.commit()
