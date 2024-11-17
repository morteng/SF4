import os
from app.models.user import User
from app.extensions import db

def init_admin_user():
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin_user')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin_password')
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

    existing_admin = User.query.filter_by(username=admin_username).first()
    if not existing_admin:
        admin = User(
            username=admin_username, 
            email=admin_email, 
            is_admin=True
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{admin_username}' created successfully.")
