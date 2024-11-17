from .models.user import User
from .extensions import db
import os

def init_admin_user():
    username = os.environ.get('ADMIN_USERNAME', 'admin_user')
    email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    password = os.environ.get('ADMIN_PASSWORD', 'admin_password')

    existing_admin = User.query.filter_by(username=username).first()
    if not existing_admin:
        admin = User(username=username, email=email, is_admin=True)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{username}' created successfully.")
    else:
        print(f"Admin user '{username}' already exists.")
