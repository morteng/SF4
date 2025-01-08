import os
import logging
from app.models.user import User
from app.models.audit_log import AuditLog
from app import db

logger = logging.getLogger(__name__)

def ensure_admin_user():
    """Ensure admin user exists in database"""
    try:
        print("Checking for admin user...")
        admin = User.query.filter_by(is_admin=True).first()
        
        if not admin:
            print("No admin found, creating new one...")
            username = os.getenv('ADMIN_USERNAME', 'admin')
            email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
            password = os.getenv('ADMIN_PASSWORD', 'admin')
            
            print(f"Creating admin with username: {username}, email: {email}")
            
            admin = User(
                username=username,
                email=email,
                is_admin=True,
                is_active=True
            )
            admin.set_password(password)
            db.session.add(admin)
            
            print("Creating audit log...")
            AuditLog.create(
                user_id=0,
                action="create_admin_user",
                details="Created default admin user from .env",
                object_type="User",
                object_id=admin.id
            )
            
            print("Committing to database...")
            db.session.commit()
            print(f"Admin user created successfully with username: {admin.username}")
        else:
            print(f"Admin user already exists (username: {admin.username})")
            
        return True
        
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if ensure_admin_user():
        print("Admin user verification passed")
        exit(0)
    else:
        print("Admin user verification failed")
        exit(1)
