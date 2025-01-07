import os
import subprocess
import logging

def deploy_to_render():
    """Deploy the application to render.com"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Verify git remote exists
        remotes = subprocess.run(["git", "remote"], capture_output=True).stdout.decode()
        if "render" not in remotes:
            logger.info("Adding render remote")
            subprocess.run(["git", "remote", "add", "render", "https://github.com/morteng/SF4"], check=True)
        
        # Ensure we are on the correct branch
        logger.info("Checking out main branch")
        subprocess.run(["git", "checkout", "main"], check=True)
        
        # Pull the latest changes
        logger.info("Pulling latest changes from origin")
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        
        # Push to render.com
        logger.info("Pushing to render.com")
        result = subprocess.run(["git", "push", "render", "main"], capture_output=True)
        if result.retcode != 0:
            logger.error(f"Push failed: {result.stderr.decode()}")
            return False
        
        logger.info("Deployment to render.com completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during deployment: {e}")
        if e.stderr:
            logger.error(f"Error details: {e.stderr.decode()}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    deploy_to_render()

if __name__ == "__main__":
    deploy_to_render()
