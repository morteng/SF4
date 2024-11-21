# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from .models.user import User
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()

def init_extensions(app):
    

    # Ensure the instance/ directory exists
    instance_path = app.instance_path
    if not os.path.exists(instance_path):
        print(f"Creating directory: {instance_path}")  # Debugging line
        os.makedirs(instance_path)

    # Ensure the database file exists
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].split('///')[-1]
    if not os.path.isfile(db_path):
        print(f"Creating database file: {db_path}")  # Debugging line
        open(db_path, 'a').close()  # Create an empty file

    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()

    # Initialize the default admin user
    init_admin_user(app)
    db.init_app(app)
    login_manager.init_app(app)

def init_admin_user(app):
    with app.app_context():
        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        email = os.environ.get('ADMIN_EMAIL')

        if not User.query.filter_by(username=username).first():
            print(f"Creating admin user: {username}")  # Debugging line
            admin_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                email=email,
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
