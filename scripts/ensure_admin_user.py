import os
import logging
from app.models.user import User
from app.models.audit_log import AuditLog
from app import db

logger = logging.getLogger(__name__)

def ensure_admin_user():
    """Ensure admin user exists in database"""
    try:
        # Check if admin user exists
        admin = User.query.filter_by(is_admin=True).first()
        
        if not admin:
            logger.info("Creating default admin user")
            admin = User(
                username=os.getenv('ADMIN_USERNAME', 'admin'),
                email=os.getenv('ADMIN_EMAIL', 'admin@example.com'),
                is_admin=True,
                is_active=True  # Ensure admin is active
            )
            admin.set_password(os.getenv('ADMIN_PASSWORD', 'admin'))
            db.session.add(admin)
            
            # Log the creation
            AuditLog.create(
                user_id=0,  # System user
                action="create_admin_user",
                details="Created default admin user from .env",
                object_type="User",
                object_id=admin.id
            )
            db.session.commit()
            logger.info(f"Admin user created successfully with username: {admin.username}")
        else:
            logger.info(f"Admin user already exists (username: {admin.username})")
            
        return True
        
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
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
