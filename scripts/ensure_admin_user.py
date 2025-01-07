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
                username=os.getenv('ADMIN_USERNAME'),
                email=os.getenv('ADMIN_EMAIL'),
                is_admin=True
            )
            admin.set_password(os.getenv('ADMIN_PASSWORD'))
            db.session.add(admin)
            
            # Log the creation
            AuditLog.create(
                user_id=0,  # System user
                action="create_admin_user",
                details="Created default admin user from .env"
            )
            db.session.commit()
            logger.info("Admin user created successfully")
        else:
            logger.info("Admin user already exists")
            
        return True
        
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if ensure_admin_user():
        print("Admin user verification passed")
        exit(0)
    else:
        print("Admin user verification failed")
        exit(1)
