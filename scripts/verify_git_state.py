import subprocess
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

def verify_git_state(pull=False, retry=3):
    """Verify git repository state is clean and up-to-date"""
    try:
        # Check for uncommitted changes
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        if status.stdout.strip():
            logger.error("Uncommitted changes detected")
            logger.info("Please commit or stash changes before proceeding")
            return False
            
        # Get current branch name
        current_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        # Verify remote exists
        remotes = subprocess.run(
            ["git", "remote"],
            capture_output=True,
            text=True
        ).stdout.splitlines()
        
        if "origin" not in remotes:
            logger.error("Origin remote not found")
            logger.info("Please add origin remote: git remote add origin <url>")
            return False
            
        # Fetch latest from origin
        for attempt in range(retry):
            try:
                subprocess.run(
                    ["git", "fetch", "origin"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                break
            except subprocess.CalledProcessError as e:
                if attempt == retry - 1:
                    logger.error(f"Failed to fetch from origin after {retry} attempts")
                    logger.info("Check your network connection and remote URL")
                    return False
                time.sleep(1)
        
        # Compare local and remote branches
        local_hash = subprocess.run(
            ["git", "rev-parse", "@"],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        remote_hash = subprocess.run(
            ["git", "rev-parse", "@{u}"],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        if local_hash != remote_hash:
            if pull:
                logger.info("Local branch not up-to-date, pulling changes")
                try:
                    subprocess.run(
                        ["git", "pull", "origin", current_branch],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    # Verify again after pull
                    local_hash = subprocess.run(
                        ["git", "rev-parse", "@"],
                        capture_output=True,
                        text=True
                    ).stdout.strip()
                    
                    if local_hash != remote_hash:
                        logger.error("Failed to sync with remote after pull")
                        logger.info("Please resolve any merge conflicts manually")
                        return False
                    return True
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to pull changes: {str(e)}")
                    logger.info("Please resolve any merge conflicts manually")
                    return False
            logger.error("Local branch is not up-to-date with remote")
            logger.info("Run with --pull flag to sync with remote")
            return False
            
        logger.info("Git state verified successfully")
        return True
    except Exception as e:
        logger.error(f"Git state verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_git_state():
        print("Git state verification passed")
        exit(0)
    else:
        print("Git state verification failed")
        exit(1)
