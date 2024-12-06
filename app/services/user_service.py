from app.models.user import User
from app.extensions import db
import os
from sqlalchemy.exc import IntegrityError
# AI: add docstrings to all functions, methods, and classes AI!

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

def update_user(user, form_data):
    user.username = form_data['username']
    user.email = form_data['email']
    user.is_admin = form_data.get('is_admin', False)
    if form_data['password']:
        user.set_password(form_data['password'])
    db.session.commit()


def ensure_default_admin_exists():
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

    user = User.query.filter_by(username=admin_username).first()
    if user is None:
        new_user = User(
            username=admin_username,
            email=admin_email,
            is_admin=True
        )
        new_user.set_password(admin_password)
        db.session.add(new_user)
        db.session.commit()
        print("Default admin user created.")
        print(admin_username)
        print(admin_email)
        print(admin_password)
    else:
        print("Default admin user already exists.")
