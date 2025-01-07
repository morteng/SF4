import os
import subprocess
import logging
import sys
from pathlib import Path

# Add scripts directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logger at module level
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def verify_deployment_checks():
    """Run all deployment verification checks"""
    try:
        from scripts.verify_deployment import verify_deployment
        if not verify_deployment('--check-security'):
            logger.error("Security verification failed")
            return False
        if not verify_deployment('--check-env'):
            logger.error("Environment verification failed")
            return False
        if not verify_deployment('--check-version'):
            logger.error("Version verification failed")
            return False
        return True
    except Exception as e:
        logger.error(f"Deployment verification failed: {str(e)}")
        return False

def deploy_to_render():
    """Deploy the application to render.com"""
    # Configure logger at module level
    global logger
    logger = configure_logger()
    
    try:
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
        
        # Verify admin user exists
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
