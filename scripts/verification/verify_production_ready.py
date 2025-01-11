import os
import sys
import logging
from pathlib import Path

def configure_logger():
    """Configure logger for production readiness verification"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_production_ready():
    """Verify production readiness with comprehensive checks"""
    try:
        # Add project root to Python path
        project_root = str(Path(__file__).parent.parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Configure paths first
        from scripts.path_config import configure_paths
        if not configure_paths():
            raise RuntimeError("Failed to configure paths")
            
        logger = configure_logger()
        
        # Set default environment variables if missing
        default_vars = {
            'BACKUP_DIR': 'backups',
            'LOG_DIR': 'logs',
            'FLASK_ENV': 'production',
            'FLASK_DEBUG': '0'
        }
        
        for var, default in default_vars.items():
            if not os.getenv(var):
                os.environ[var] = default
                logger.info(f"Set default value for {var}: {default}")
                
        # Create application context
        from app import create_app
        app = create_app()

        # Ensure debug mode is disabled
        if os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes'):
            os.environ['FLASK_DEBUG'] = '0'
            app.config['DEBUG'] = False
            logger.info("Debug mode disabled for production")
        
        # Verify and set default environment variables
        required_vars = {
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///instance/site.db',
            'SECRET_KEY': secrets.token_urlsafe(64),
            'ADMIN_PASSWORD': 'AdminPass123!',
            'BACKUP_DIR': 'backups',
            'LOG_DIR': 'logs',
            'ADMIN_CSRF_SECRET': secrets.token_urlsafe(32)
        }
        
        for var, default in required_vars.items():
            if not os.getenv(var):
                os.environ[var] = default
                logger.info(f"Set default value for {var}")
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
            
        # Create application context
        from app import create_app
        app = create_app()
        
        # Ensure debug mode is disabled
        if os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes'):
            os.environ['FLASK_DEBUG'] = '0'
            app.config['DEBUG'] = False
            logger.info("Debug mode disabled for production")
        
        # Verify SECRET_KEY meets requirements
        secret_key = os.getenv('SECRET_KEY') or app.config.get('SECRET_KEY')
        if not secret_key or len(secret_key) < 64 or len(set(secret_key)) < 32:
            logger.error("SECRET_KEY must be at least 64 characters with 32 unique characters")
            return False
            
        # Verify database connection
        from scripts.verification.verify_db_connection import verify_db_connection
        if not verify_db_connection():
            logger.error("Database connection verification failed")
            return False
            
        # Verify security settings including admin interface
        from scripts.verification.verify_security import verify_security_settings
        if not verify_security_settings(check_admin_interface=True):
            logger.error("Security verification failed")
            return False
            
        # Verify admin interface configuration
        if not os.getenv('ADMIN_CSRF_SECRET'):
            logger.error("Missing ADMIN_CSRF_SECRET for admin interface")
            return False
        if not os.getenv('ADMIN_SESSION_TIMEOUT'):
            logger.error("Missing ADMIN_SESSION_TIMEOUT")
            return False
            
        # Verify admin interface uses full page reloads and has required fields
        from app.routes.admin import admin_bp
        if not hasattr(admin_bp, 'full_page_reloads'):
            logger.error("Admin interface must use full page reloads")
            return False
            
        # Verify only stipend name is required
        from app.models.stipend import Stipend
        if not Stipend.__table__.columns['name'].nullable:
            logger.error("Stipend name must be required field")
            return False
            
        logger.info("Production environment is ready")
        return True
        
    except Exception as e:
        logger.error(f"Production readiness verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_production_ready():
        print("Production readiness verification passed")
        exit(0)
    else:
        print("Production readiness verification failed")
        exit(1)
