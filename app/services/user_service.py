from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.extensions import db
from app.utils import flash_message
from app.constants import FlashMessages, FlashCategory

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
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"{FlashMessages.USERNAME_ALREADY_EXISTS.value}: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"{FlashMessages.CREATE_USER_ERROR.value}{str(e)}")
    
    return new_user

def update_user(user, form_data):
    print(f"Updating user with data: {form_data}")  # Debug statement
    new_username = form_data['username']
    
    # Check for duplicate username
    if new_username != user.username:
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user:
            raise ValueError(FlashMessages.USERNAME_ALREADY_EXISTS.value)
    
    user.username = new_username
    user.email = form_data['email']
    if 'password' in form_data and form_data['password']:
        user.set_password(form_data['password'])
    user.is_admin = form_data.get('is_admin', False)
    
    try:
        db.session.commit()
        flash_message(FlashMessages.PROFILE_UPDATE_SUCCESS, FlashCategory.SUCCESS)
        print(f"User {user.username} updated successfully.")  # Debug statement
    except Exception as e:
        flash_message(FlashMessages.PROFILE_UPDATE_FAILED, FlashCategory.ERROR)
        print(f"Failed to update user: {e}")  # Debug statement
        db.session.rollback()
        raise ValueError("Failed to update user.")
