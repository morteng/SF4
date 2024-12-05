from app.models.user import User
from app.extensions import db
import os
from sqlalchemy.exc import IntegrityError  # Import IntegrityError

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
    is_admin = form_data.get('is_admin', False)  # Accept is_admin parameter

    new_user = User(username=username, email=email, is_admin=is_admin)  # Set is_admin attribute
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:  # IntegrityError is now defined
        db.session.rollback()
        raise ValueError("Username or email already exists")
    
    return new_user

def update_user(user):
    db.session.commit()

def ensure_default_admin_exists():
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')  # This should be hashed and secure in production

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
