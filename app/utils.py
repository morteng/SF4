import os
from flask import current_app as app
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.extensions import db

def init_admin_user():
    # Use os.environ.get() with a default to ensure we always have a value
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    password = os.environ.get('ADMIN_PASSWORD', 'defaultpassword')
    email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

    admin_user = User.query.filter_by(username=username).first()
    if not admin_user:
        admin_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            email=email,
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"Created admin user: {username}")
