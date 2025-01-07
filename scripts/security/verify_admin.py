import os
from app.models.user import User
from app.extensions import db
import logging

logger = logging.getLogger(__name__)

def verify_admin_user():
    """Ensure admin user exists, create from .env if missing"""
    try:
        # Check if admin user exists
        admin = User.query.filter_by(is_admin=True).first()
        
        if not admin:
            # Create admin from .env variables
            admin = User(
                username=os.getenv('ADMIN_USERNAME'),
                email=os.getenv('ADMIN_EMAIL'),
                password=os.getenv('ADMIN_PASSWORD'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("Created default admin user from .env")
        return True
    except Exception as e:
        logger.error(f"Failed to verify admin user: {str(e)}")
        return False

if __name__ == "__main__":
    if verify_admin_user():
        print("Admin user verification passed")
        exit(0)
    else:
        print("Admin user verification failed")
        exit(1)
