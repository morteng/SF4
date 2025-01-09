import subprocess
import logging
from pathlib import Path
import sys

def configure_logging():
    """Configure logging for commit script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/commit.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def commit_changes(message, push=False):
    """Commit pending changes with provided message"""
    logger = configure_logging()
    
    try:
        # Configure paths first
        from scripts.path_config import configure_paths
        if not configure_paths():
            logger.error("Path configuration failed")
            return False
    
    try:
        # Verify git status first
        status = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True
        )
        
        if not status.stdout.strip():
            logger.info("No changes to commit")
            return True
            
        # Stage all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit with message
        subprocess.run(['git', 'commit', '-m', message], check=True)
        
        # Push changes if requested
        if push:
            subprocess.run(['git', 'push'], check=True)
            logger.info(f"Successfully committed and pushed changes: {message}")
        else:
            logger.info(f"Successfully committed changes: {message}")
            
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Commit failed: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == '--message':
        message = sys.argv[2]
        if commit_changes(message):
            exit(0)
    exit(1)
