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
    is_admin = form_data.get('is_admin', False)  # Accept is_admin parameter

    new_user = User(username=username, email=email, is_admin=is_admin)  # Set is_admin attribute
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

def ensure_default_admin_exists():
    admin_username = 'admin'
    admin_email = 'admin@example.com'
    admin_password = 'admin123'  # This should be hashed and secure in production
    admin_is_admin = True

    user = User.query.filter_by(username=admin_username).first()
    if user is None:
        new_user = User(
            username=admin_username,
            email=admin_email,
            is_admin=admin_is_admin
        )
        new_user.set_password(admin_password)
        db.session.add(new_user)
        db.session.commit()
        print("Default admin user created.")
    else:
        print("Default admin user already exists.")
