import os
import subprocess
import logging
import sys
from pathlib import Path

# Configure paths first
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.path_config import configure_paths
if not configure_paths():
    print("Path configuration failed")
    exit(1)

# Now we can safely import app modules
from flask import Flask
from app import create_app

# Configure logger at module level
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Configure paths first
from scripts.path_config import configure_paths
if not configure_paths():
    logger.error("Path configuration failed")
    exit(1)

# Now we can safely import app modules
from app import create_app

from scripts.version import validate_version, get_version

# Configure logger at module level
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def verify_deployment_checks():
    """Run all deployment verification checks"""
    app = create_app()  # Create application instance
    with app.app_context():  # Establish application context
        try:
            # Verify test coverage
            from scripts.verify_test_coverage import verify_coverage
            if not verify_coverage():
                logger.error("Test coverage verification failed")
                return False
                
            # Verify version
            version = get_version()
            if not validate_version(version):
                logger.error("Version verification failed")
                return False
                
            # Verify environment variables
            required_vars = [
                'SQLALCHEMY_DATABASE_URI',
                'SECRET_KEY',
                'ADMIN_USERNAME',
                'ADMIN_PASSWORD',
                'RENDER_API_KEY'
            ]
            
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
                return False
                
            # Verify SECRET_KEY complexity
            secret_key = os.getenv('SECRET_KEY')
            if len(secret_key) < 64:
                logger.error("SECRET_KEY must be at least 64 characters")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Deployment verification failed: {str(e)}")
            return False

def handle_render_api_errors(response):
    """Handle Render API specific errors"""
    if response.status_code == 401:
        logger.error("Render API authentication failed - check RENDER_API_KEY")
        return False
    elif response.status_code == 429:
        logger.error("Render API rate limit exceeded")
        return False
    elif response.status_code >= 500:
        logger.error("Render API server error")
        return False
    return True

def deploy_to_render():
    """Deploy the application to render.com"""
    app = create_app()  # Create application instance
    
    try:
        # Verify we have API key
        if not os.getenv('RENDER_API_KEY'):
            logger.error("RENDER_API_KEY not found in environment variables")
            return False
        # Verify deployment checklist
        from scripts.verify_deployment import verify_deployment
        logger.info("Starting full deployment verification")
        
        # Run security checks
        if not verify_deployment('--check-security'):
            logger.error("Security verification failed")
            return False
            
        # Run environment checks
        if not verify_deployment('--check-env'):
            logger.error("Environment verification failed")
            return False
            
        # Run version checks
        if not verify_deployment('--check-version'):
            logger.error("Version verification failed")
            return False
            
        logger.info("All deployment verifications passed")
        
        # Verify database connection
        from scripts.verify_db_connection import verify_db_connection
        if not verify_db_connection():
            logger.error("Database connection verification failed")
            return False
        logger.info("Database connection verified")
        
        # Verify admin user exists within app context
        with app.app_context():
            from scripts.startup.init_admin import initialize_admin_user
            if not initialize_admin_user():
                logger.error("Admin user verification failed")
                return False
            logger.info("Admin user verified")
            
        # Verify version file
        from scripts.version import validate_version
        if not validate_version():
            logger.error("Version validation failed")
            return False
            
        # Verify git remote exists
        remotes = subprocess.run(["git", "remote"], capture_output=True, text=True).stdout
        if "render" not in remotes:
            logger.info("Adding render remote")
            subprocess.run(
                ["git", "remote", "add", "render", "https://github.com/morteng/SF4"], 
                check=True
            )
        
        # Ensure we are on the correct branch
        logger.info("Checking out main branch")
        subprocess.run(["git", "checkout", "main"], check=True)
        
        # Pull the latest changes
        logger.info("Pulling latest changes from origin")
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        
        # Push to render.com
        logger.info("Pushing to render.com")
        result = subprocess.run(
            ["git", "push", "render", "main"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Push failed: {result.stderr}")
            return False
            
        logger.info("Deployment to render.com completed successfully.")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during deployment: {e}")
        if e.stderr:
            logger.error(f"Error details: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    sys.exit(0 if deploy_to_render() else 1)
