import os
import traceback
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.extensions import db

def init_admin_user():
    try:
        # Print out environment variables for debugging
        print("Environment Variables:")
        print(f"ADMIN_USERNAME: {os.environ.get('ADMIN_USERNAME')}")
        print(f"ADMIN_EMAIL: {os.environ.get('ADMIN_EMAIL')}")
        
        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        email = os.environ.get('ADMIN_EMAIL')

        if not all([username, password, email]):
            raise ValueError("Admin credentials are incomplete. Please check your environment variables.")

        # Add more detailed query and session management
        print("Querying for existing admin user...")
        admin_user = User.query.filter_by(username=username).first()
        
        if not admin_user:
            print("Creating new admin user...")
            admin_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                email=email,
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user '{username}' created successfully.")
        else:
            print(f"Admin user '{username}' already exists.")
    
    except Exception as e:
        print("Error in init_admin_user:")
        print(traceback.format_exc())
        raise

def add_numbers(a, b):
    return a + b

def subtract_numbers(a, b):
    return a - b
