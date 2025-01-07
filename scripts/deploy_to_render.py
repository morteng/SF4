import os
import subprocess
import logging
import sys
from pathlib import Path

# Add scripts directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

def configure_logger():
    """Configure the logger consistently across the module"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def deploy_to_render():
    """Deploy the application to render.com"""
    logger = logging.getLogger(__name__)
    
    try:
        # Verify deployment checklist
        from scripts.verify_deployment import verify_deployment
        logger.info("Starting deployment verification")
        if not verify_deployment():
            logger.error("Deployment verification failed")
            return False
        logger.info("Deployment verification passed")
            
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
