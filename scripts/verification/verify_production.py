import os
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine, inspect
from alembic.config import Config
from alembic import command
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def configure_logger():
    """Ensure logger is properly configured."""
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = configure_logger()

def verify_database_connection(db_url):
    """Verify database connection and schema version."""
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            inspector = inspect(engine)
            if 'alembic_version' not in inspector.get_table_names():
                logger.error("Alembic version table not found")
                return False

            version = conn.execute("SELECT version_num FROM alembic_version").scalar()
            logger.info(f"Current database version: {version}")
            return True

    except Exception as e:
        logger.error("Database connection error", exc_info=True)
        return False

def verify_alembic_migrations(config_path="migrations/alembic.ini"):
    """Verify Alembic migrations are up to date."""
    if not Path(config_path).exists():
        logger.error(f"Alembic configuration file not found: {config_path}")
        return False

    try:
        alembic_cfg = Config(config_path)
        command.upgrade(alembic_cfg, 'head')
        return True
    except Exception as e:
        logger.error("Alembic migration error", exc_info=True)
        return False

def verify_environment_variables(required_vars):
    """Verify required environment variables are set."""
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False

    for var in required_vars:
        logger.info(f"{var}: {os.getenv(var)}")

    return True

def check_complexity(value, min_length=12):
    """Check complexity requirements for a string."""
    checks = [
        (len(value) >= min_length, f"at least {min_length} characters"),
        (any(c.isupper() for c in value), "an uppercase letter"),
        (any(c.islower() for c in value), "a lowercase letter"),
        (any(c.isdigit() for c in value), "a digit"),
        (any(c in '!@#$%^&*()_+-=[]{};:,.<>?/"' for c in value), "a special character")
    ]

    for check, requirement in checks:
        if not check:
            return False, requirement

    return True, None

def verify_security_settings():
    """Verify security-related settings."""
    try:
        # Debug mode check
        if os.getenv('FLASK_DEBUG') == '1':
            logger.error("Debug mode must be disabled in production")
            return False

        # SECRET_KEY validation
        secret_key = os.getenv('SECRET_KEY', '')
        is_valid, requirement = check_complexity(secret_key, min_length=64)
        if not is_valid:
            logger.error(f"SECRET_KEY must contain {requirement}")
            return False

        # ADMIN_PASSWORD validation
        admin_password = os.getenv('ADMIN_PASSWORD', '')
        is_valid, requirement = check_complexity(admin_password)
        if not is_valid:
            logger.error(f"ADMIN_PASSWORD must contain {requirement}")
            return False

        # ADMIN_EMAIL validation
        admin_email = os.getenv('ADMIN_EMAIL')
        if not admin_email or '@' not in admin_email:
            logger.error("Invalid ADMIN_EMAIL format")
            return False

        return True

    except Exception as e:
        logger.error("Security verification error", exc_info=True)
        return False

def verify_logs_directory():
    """Verify logs directory structure exists."""
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
        logger.error("Logs directory verification error", exc_info=True)
        return False

def main():
    """Main verification function."""
    logger.info("Starting production verification...")

    # Required environment variables
    required_vars = [
        'SQLALCHEMY_DATABASE_URI',
        'SECRET_KEY',
        'ADMIN_EMAIL',
        'ADMIN_PASSWORD',
        'FLASK_ENV',
        'FLASK_DEBUG'
    ]

    # Step-by-step verification
    if not verify_environment_variables(required_vars):
        sys.exit(1)

    if not verify_security_settings():
        sys.exit(1)

    db_url = os.getenv('SQLALCHEMY_DATABASE_URI')
    if not db_url or not verify_database_connection(db_url):
        sys.exit(1)

    if not verify_alembic_migrations():
        sys.exit(1)

    if not verify_logs_directory():
        sys.exit(1)

    logger.info("Production verification completed successfully")
    sys.exit(0)

if __name__ == "__main__":
    main()
