import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def verify_git_state(sync=False, pull=False):
    """Verify git repository is in clean state"""
    try:
        # Check for uncommitted changes
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        if status.stdout.strip():
            logger.error("Uncommitted changes detected")
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
            return False
            
        # Fetch latest from origin
        subprocess.run(
            ["git", "fetch", "origin"],
            check=True
        )
        
        # Compare local and remote branches
        local_hash = subprocess.run(
            ["git", "rev-parse", current_branch],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        remote_hash = subprocess.run(
            ["git", "rev-parse", f"origin/{current_branch}"],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        if local_hash != remote_hash:
            if pull:
                logger.info("Local branch not up to date, pulling changes...")
                subprocess.run(
                    ["git", "pull", "origin", current_branch],
                    check=True
                )
                return True
            logger.error("Local branch is not up to date with remote")
            return False
            
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
