import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def verify_git_state():
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
            
        # Verify branch is up to date
        subprocess.run(["git", "fetch"], check=True)
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
        
        if local != remote:
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
