import sys
import os
import logging
from pathlib import Path

# Configure logger
logger = logging.getLogger("deployment_verification")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Attempt to import and configure paths once
try:
    from scripts.path_config import configure_paths
except ImportError as e:
    logger.error(f"Failed to import path configuration module: {e}")
    sys.exit(1)

if not configure_paths():
    logger.error("Path configuration failed")
    sys.exit(1)

# Helper Functions
def validate_complexity(secret_key):
    """Validate the complexity of the secret key."""
    complexity_checks = [
        (any(c.isupper() for c in secret_key), "uppercase letter"),
        (any(c.islower() for c in secret_key), "lowercase letter"),
        (any(c.isdigit() for c in secret_key), "digit"),
        (any(c in '!@#$%^&*()_+-=[]{};:,.<>?/' for c in secret_key), "special character")
    ]
    for check, requirement in complexity_checks:
        if not check:
            return False, requirement
    return True, None

def validate_environment_variables(required_vars):
    """Check for the presence of required environment variables."""
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    return True

# Verification Functions
def verify_environment():
    """Verify required environment variables are set."""
    required_vars = ['FLASK_ENV', 'FLASK_DEBUG', 'SQLALCHEMY_DATABASE_URI', 'SECRET_KEY']
    return validate_environment_variables(required_vars)

def verify_security_settings():
    """Verify security-related settings."""
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key or len(secret_key) < 64:
        logger.error("SECRET_KEY must be at least 64 characters")
        return False

    is_valid, failed_check = validate_complexity(secret_key)
    if not is_valid:
        logger.error(f"SECRET_KEY must contain at least one {failed_check}")
        return False

    insecure_patterns = ['password', '123456', 'qwerty', 'admin', 'secret']
    if any(pattern.lower() in secret_key.lower() for pattern in insecure_patterns):
        logger.error("SECRET_KEY contains insecure patterns")
        return False

    secret_key_history_path = Path('.secret_key_history')
    if secret_key_history_path.exists():
        with secret_key_history_path.open() as f:
            if secret_key in f.read():
                logger.error("SECRET_KEY has not been rotated recently")
                return False

    return True

def verify_version():
    """Verify version file exists and is valid."""
    try:
        from scripts.version import validate_version, get_version
        version = get_version()
        if not validate_version(version):
            logger.error("Version validation failed")
            return False
        return True
    except ImportError as e:
        logger.error(f"Failed to import version validation module: {e}")
        return False
    except Exception as e:
        logger.error(f"Version verification failed: {str(e)}")
        return False

def verify_db_connection():
    """Verify database connection."""
    try:
        from scripts.verify_db_connection import verify_db_connection as verify_db
        return verify_db()
    except ImportError as e:
        logger.error(f"Failed to import database connection verification module: {e}")
        return False
    except Exception as e:
        logger.error(f"Database connection verification failed: {str(e)}")
        return False

def verify_deployment(verify_paths=True):
    """
    Verify all deployment settings and configurations.
    If verify_paths is True, re-run path configuration checks in production mode.
    """
    logger.info("Starting deployment verification")

    if verify_paths:
        # Re-run path config in production/verification mode
        if not configure_paths(production=True, verify=True):
            logger.error("Path configuration failed")
            return False

    # Do environment verification first, so we don’t blow up on missing vars
    if not verify_environment():
        logger.error("Environment verification failed")
        return False

    if not verify_security_settings():
        logger.error("Security settings verification failed")
        return False

    if not verify_version():
        logger.error("Version verification failed")
        return False

    if not verify_db_connection():
        logger.error("Database connection verification failed")
        return False

    logger.info("Deployment verification passed")
    return True

if __name__ == "__main__":
    if verify_deployment():
        print("Deployment verification passed")
        sys.exit(0)
    else:
        print("Deployment verification failed")
        sys.exit(1)
