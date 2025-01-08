import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def sync_branch():
    """Sync local branch with remote"""
    try:
        # Fetch all changes
        subprocess.run(["git", "fetch", "--all"], check=True)
        
        # Reset to remote branch
        subprocess.run(["git", "reset", "--hard", "@{u}"], check=True)
        
        # Clean untracked files
        subprocess.run(["git", "clean", "-fd"], check=True)
        return True
    except Exception as e:
        logger.error(f"Branch synchronization failed: {str(e)}")
        return False

def verify_sync():
    """Verify branch is synchronized with remote"""
    try:
        # Get local and remote commit hashes
        local = subprocess.run(
            ["git", "rev-parse", "@"],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        remote = subprocess.run(
            ["git", "rev-parse", "@{u}"],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        return local == remote
    except Exception as e:
        logger.error(f"Sync verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if not verify_sync():
        logger.info("Branch out of sync, attempting to sync...")
        if sync_branch():
            print("Branch synchronization successful")
            exit(0)
        else:
            print("Branch synchronization failed")
            exit(1)
    else:
        print("Branch already synchronized")
        exit(0)
