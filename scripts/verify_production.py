import os
import sys
import subprocess
from pathlib import Path
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_database_connection(db_url):
    """Verify database connection and schema version"""
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            inspector = inspect(engine)
            if 'alembic_version' not in inspector.get_table_names():
                logger.error("Alembic version table not found")
                return False
                
            result = conn.execute("SELECT version_num FROM alembic_version")
            version = result.scalar()
            logger.info(f"Current database version: {version}")
            return True
            
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False

def verify_alembic_migrations():
    """Verify Alembic migrations are up to date"""
    try:
        alembic_cfg = Config("migrations/alembic.ini")
        command.upgrade(alembic_cfg, 'head')
        return True
    except Exception as e:
        logger.error(f"Alembic migration error: {str(e)}")
        return False

def verify_environment_variables():
    """Verify required environment variables are set"""
    required_vars = [
        'SQLALCHEMY_DATABASE_URI',
        'SECRET_KEY',
        'ADMIN_EMAIL',
        'ADMIN_PASSWORD',
        'FLASK_ENV',
        'FLASK_DEBUG'
    ]
    
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    for var in required_vars:
        logger.info(f"{var}: {os.environ[var]}")
    
    return True

def verify_security_settings():
    """Verify security-related settings"""
    try:
        # Check debug mode
        if os.getenv('FLASK_DEBUG') == '1':
            logger.warning("Debug mode is enabled in production")
            return False
            
        # Verify SECRET_KEY
        secret_key = os.getenv('SECRET_KEY', '')
        if len(secret_key) < 64:
            logger.error(f"SECRET_KEY is too short (length: {len(secret_key)}), minimum 64 characters required")
            return False
            
        # Verify ADMIN_PASSWORD
        admin_password = os.getenv('ADMIN_PASSWORD', '')
        if len(admin_password) < 12:
            logger.error("ADMIN_PASSWORD must be at least 12 characters long")
            logger.info("Please update ADMIN_PASSWORD in .env file")
            return False
            
        # Verify password complexity
        complexity_checks = [
            (any(c.isupper() for c in admin_password), "uppercase letter"),
            (any(c.islower() for c in admin_password), "lowercase letter"),
            (any(c.isdigit() for c in admin_password), "digit"),
            (any(c in '!@#$%^&*()_+-=[]{};:,.<>?/' for c in admin_password), "special character")
        ]
        
        for check, requirement in complexity_checks:
            if not check:
                logger.error(f"ADMIN_PASSWORD must contain at least one {requirement}")
                return False
            
        # Verify SECRET_KEY complexity
        complexity_checks = [
            (any(c.isupper() for c in secret_key), "uppercase letter"),
            (any(c.islower() for c in secret_key), "lowercase letter"),
            (any(c.isdigit() for c in secret_key), "digit"),
            (any(c in "!@#$%^&*()_+-=[]{};':,.<>?/" for c in secret_key), "special character")
        ]
        
        for check, requirement in complexity_checks:
            if not check:
                logger.error(f"SECRET_KEY must contain at least one {requirement}")
                return False
            
        # Verify SECRET_KEY complexity
        complexity_checks = [
            (any(c.isupper() for c in secret_key), "uppercase letter"),
            (any(c.islower() for c in secret_key), "lowercase letter"),
            (any(c.isdigit() for c in secret_key), "digit"),
            (any(c in "!@#$%^&*()_+-=[]{};':,.<>?/" for c in secret_key), "special character")
        ]
        
        for check, requirement in complexity_checks:
            if not check:
                logger.error(f"SECRET_KEY must contain at least one {requirement}")
                return False
            
        # Verify SECRET_KEY complexity
        complexity_checks = [
            (any(c.isupper() for c in secret_key), "uppercase letter"),
            (any(c.islower() for c in secret_key), "lowercase letter"), 
            (any(c.isdigit() for c in secret_key), "digit"),
            (any(c in "!@#$%^&*()_+-=[]{};':,.<>?/" for c in secret_key), "special character")
        ]
        
        for check, requirement in complexity_checks:
            if not check:
                logger.error(f"SECRET_KEY must contain at least one {requirement}")
                return False
            
        # Verify SECRET_KEY rotation
        if os.path.exists('.secret_key_history'):
            with open('.secret_key_history') as f:
                if secret_key in f.read():
                    logger.error("SECRET_KEY has not been rotated recently")
                    return False
            
        # Verify SECRET_KEY complexity
        if not any(c.isupper() for c in secret_key):
            logger.error("SECRET_KEY must contain at least one uppercase letter")
            return False
        if not any(c.islower() for c in secret_key):
            logger.error("SECRET_KEY must contain at least one lowercase letter")
            return False
        if not any(c.isdigit() for c in secret_key):
            logger.error("SECRET_KEY must contain at least one digit")
            return False
        if not any(c in "!@#$%^&*()_+-=[]{};':,.<>?/" for c in secret_key):
            logger.error("SECRET_KEY must contain at least one special character")
            return False
            
        # Verify admin credentials
        admin_email = os.getenv('ADMIN_EMAIL')
        if not admin_email or '@' not in admin_email:
            logger.error("Invalid ADMIN_EMAIL format")
            return False
            
        admin_password = os.getenv('ADMIN_PASSWORD')
        if not admin_password or len(admin_password) < 12:
            logger.error("ADMIN_PASSWORD must be at least 12 characters long")
            return False
            
        # Verify SECRET_KEY complexity
        if not any(c.isupper() for c in secret_key) or \
           not any(c.islower() for c in secret_key) or \
           not any(c.isdigit() for c in secret_key):
            logger.error("SECRET_KEY must contain uppercase, lowercase and numbers")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Security verification error: {str(e)}")
        return False

def verify_logs_directory():
    """Verify logs directory structure exists"""
    try:
        logs_dir = Path('logs')
        if not logs_dir.exists():
            logger.error("Logs directory not found")
            return False
            
        required_subdirs = ['app', 'tests', 'bots']
        for subdir in required_subdirs:
            if not (logs_dir / subdir).exists():
                logger.error(f"Missing logs subdirectory: {subdir}")
                return False
                
        return True
    except Exception as e:
        logger.error(f"Logs directory verification error: {str(e)}")
        return False

def main():
    """Main verification function"""
    logger.info("Starting production verification...")
    
    # Get database URL from environment
    db_url = os.getenv('SQLALCHEMY_DATABASE_URI')
    if not db_url:
        logger.error("SQLALCHEMY_DATABASE_URI not set")
        sys.exit(1)
        
    # Run verification steps
    if not verify_environment_variables():
        sys.exit(1)
        
    if not verify_security_settings():
        sys.exit(1)
        
    if not verify_database_connection(db_url):
        sys.exit(1)
        
    if not verify_alembic_migrations():
        sys.exit(1)
        
    if not verify_logs_directory():
        sys.exit(1)
        
    logger.info("Production verification completed successfully")
    sys.exit(0)

if __name__ == "__main__":
    main()
