from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.extensions import db
from flask import flash

def get_user_by_id(user_id):
    return db.session.get(User, user_id)

def delete_user(user):
    if not user:
        raise ValueError("User does not exist.")
    db.session.delete(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ValueError("Failed to delete user.")

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
        flash("Username or email already exists", 'danger')
        raise ValueError("Username or email already exists")
    except Exception as e:
        db.session.rollback()
        flash("Failed to create user.", 'danger')  # Flash the error message
        raise ValueError("Failed to create user.")
    
    return new_user
