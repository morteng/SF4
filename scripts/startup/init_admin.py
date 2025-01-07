import os
import logging
from pathlib import Path
from app.models.user import User
from app.models.audit_log import AuditLog
from app import db

logger = logging.getLogger(__name__)

def initialize_admin_user():
    """Initialize admin user from environment variables"""
    logger = logging.getLogger(__name__)
    try:
        # Verify ADMIN_PASSWORD length
        admin_password = os.getenv('ADMIN_PASSWORD')
        if len(admin_password) < 12:
            logger.error("ADMIN_PASSWORD must be at least 12 characters")
            return False
            
        # Check if admin user exists
        admin = User.query.filter_by(is_admin=True).first()
        
        if admin:
            logger.info("Admin user already exists")
            return True
            
        # Create new admin user from environment variables
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
        return True
        
    except Exception as e:
        logger.error(f"Error initializing admin user: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if initialize_admin_user():
        print("Admin user initialization successful")
        exit(0)
    else:
        print("Admin user initialization failed")
        exit(1)