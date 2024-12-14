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

def update_user(user, form_data):
    print(f"Updating user with data: {form_data}")  # Debug statement
    user.username = form_data['username']
    user.email = form_data['email']
    if 'password' in form_data and form_data['password']:
        user.set_password(form_data['password'])
    user.is_admin = form_data.get('is_admin', False)
    
    try:
        db.session.commit()
        flash("User updated successfully.", 'success')  # Flash the success message
        print(f"User {user.username} updated successfully.")  # Debug statement
    except Exception as e:
        flash("Failed to update user.", 'danger')  # Flash the error message
        print(f"Failed to update user: {e}")  # Debug statement
        db.session.rollback()  # Add this line to rollback the session
        raise ValueError("Failed to update user.")
