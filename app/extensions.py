# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from .models.user import User
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()

def init_extensions(app):
    print("Initializing extensions...")  # Debugging line
    db.init_app(app)
    login_manager.init_app(app)

    # Ensure the instance/ directory exists
    instance_path = app.instance_path
    if not os.path.exists(instance_path):
        print(f"Creating directory: {instance_path}")  # Debugging line
        os.makedirs(instance_path)


def init_admin_user(app):
    username = os.environ.get('ADMIN_USERNAME')
    password = os.environ.get('ADMIN_PASSWORD')
    email = os.environ.get('ADMIN_EMAIL')

    if not User.query.filter_by(username=username).first():
        print(f"Creating admin user: {username}")  # Debugging line
        admin_user = User(
            username=username,
            email=email,
            is_admin=True
        )
        admin_user.set_password(password)
        db.session.add(admin_user)
        db.session.commit()
